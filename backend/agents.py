"""
GRWM - Agentic AI System for GitHub README Generation
Uses LangGraph with modern patterns: conditional routing, parallel execution, checkpointing
"""

import os
import asyncio
from typing import TypedDict, Annotated, Optional, List, Dict, Any
from operator import add
from concurrent.futures import ThreadPoolExecutor
import threading

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# Import our GitHub tools
from main import (
    GitHubAPIClient,
    ProfileDetective,
    RepositoryStalker,
    ExReadme,
    TechStackDetective,
    SocialProofCollector,
    LanguageAnalyzer,
    ContributionCalendar,
    SkillExtractor,
)

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_PAT")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# ============================================================
# STATE DEFINITION (with best practices)
# ============================================================

class AgentState(TypedDict):
    """State that flows through the entire agent graph"""
    # Input
    username: str
    user_preferences: Optional[Dict[str, Any]]  # tone, style, sections

    # Data Layer (Detective's output)
    raw_data: Optional[Dict[str, Any]]

    # Analysis Layer (CTO's output)
    analysis: Optional[Dict[str, Any]]

    # Output Layer (Ghostwriter's output)
    final_markdown: Optional[str]

    # Messaging (LangGraph's message reducer pattern)
    messages: Annotated[List[BaseMessage], add_messages]

    # Error Handling
    error: Optional[str]
    retry_count: int

    # Debugging & Streaming
    intermediate_results: Optional[Dict[str, Any]]

    # Revision Support
    revision_instructions: Optional[str]
    generation_history: List[str]


# ============================================================
# INITIALIZE LLM (Gemini Flash - Free Tier)
# ============================================================

def create_llm(temperature: float = 0.7):
    """Initialize Gemini model"""
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # Latest free model (Dec 2025)
        temperature=temperature,
        google_api_key=GOOGLE_API_KEY,
    )


# ============================================================
# AGENT 1: THE DETECTIVE (Data Fetcher)
# ============================================================

class DetectiveAgent:
    """
    Responsible for fetching ALL raw data from GitHub
    Uses parallel execution for speed
    """

    def __init__(self, github_token: str, progress_callback=None):
        self.client = GitHubAPIClient(github_token)
        self.profile_detective = ProfileDetective(self.client)
        self.repo_stalker = RepositoryStalker(self.client)
        self.ex_readme = ExReadme(self.client)
        self.tech_detective = TechStackDetective(self.client)
        self.llm = create_llm(temperature=0.3)  # Low temp for factual tasks
        self.progress_callback = progress_callback

    async def investigate_parallel(self, username: str) -> Dict[str, Any]:
        """
        Fetch data in parallel for maximum speed
        """
        print(
            f"\n🔍 THE DETECTIVE: Time to stalk... I mean, investigate @{username}...")

        try:
            # Step 1: Get profile (required first)
            msg = "🕵️ Digging up the basics (legally, of course)..."
            print(f"  ├─ {msg}")
            if self.progress_callback:
                self.progress_callback("detective", msg)

            profile = self.profile_detective.investigate(username)
            msg = f"Found: {profile['basic_info']['name'] or username} - {profile['stats']['followers']} followers (popular kid!)"
            print(f"  │   {msg}")
            if self.progress_callback:
                self.progress_callback("detective", msg)

            # Step 2: Run other fetches in parallel
            msg = "🚀 Going full speed ahead with parallel snooping..."
            print(f"  ├─ {msg}")
            if self.progress_callback:
                self.progress_callback("detective", msg)

            # These can run simultaneously
            existing_readme_task = asyncio.to_thread(
                self.ex_readme.read, username
            )

            # These need profile data first but can run in parallel with each other
            enhanced_repos_task = asyncio.to_thread(
                self._get_enhanced_repos,
                username,
                profile["repositories"],
                profile["pinned_repos"]
            )

            # Wait for both
            existing_readme, enhanced_repos = await asyncio.gather(
                existing_readme_task,
                enhanced_repos_task
            )
            msg = f"Gathered {len(enhanced_repos)} repos. Quality > Quantity (we hope)."
            print(f"  │   {msg}")
            if self.progress_callback:
                self.progress_callback("detective", msg)

            msg = "🔬 CSI-level analysis of tech stacks..."
            print(f"  ├─ {msg}")
            if self.progress_callback:
                self.progress_callback("detective", msg)

            # Show pinned repos first
            pinned_repo_names = [repo['name']
                                 for repo in profile["pinned_repos"]]
            if pinned_repo_names:
                msg = f"📌 Pinned repos: {', '.join(pinned_repo_names[:3])}{' +more' if len(pinned_repo_names) > 3 else ''}"
                print(f"  │   {msg}")
                if self.progress_callback:
                    self.progress_callback("detective", msg)

            # Tech stack detection (needs enhanced_repos)
            enriched_repos = await asyncio.to_thread(
                self.tech_detective.investigate_repos,
                username,
                enhanced_repos,
                self.progress_callback  # Pass callback to show repo investigation
            )

            # Calculate social proof (can use enhanced_repos)
            social_proof = SocialProofCollector.collect(
                enriched_repos, profile)
            msg = f"Total clout: {social_proof['total_stars']} ⭐ | Apparently people like this."
            print(f"  │   {msg}")
            if self.progress_callback:
                self.progress_callback("detective", msg)

            if existing_readme:
                print(
                    "  ├─ 📄 Found existing README. They're not a complete noob!")
            else:
                print("  ├─ 📄 No README found. That's why we're here, right?")

            print(
                "  └─ ✅ Investigation complete! Time to analyze this digital footprint.")

            return {
                "profile": profile["basic_info"],
                "stats": profile["stats"],
                "contributions": profile["contributions"],
                "repositories": enriched_repos,
                "pinned_repos": profile["pinned_repos"],
                "social_proof": social_proof,
                "social_accounts": profile["social_accounts"],
                "existing_readme": existing_readme,
            }

        except Exception as e:
            print(f"  └─ ❌ Investigation failed: {e}")
            raise

    def _get_enhanced_repos(self, username: str, repositories: List[Dict], pinned_repos: List[Dict]) -> List[Dict]:
        """Helper to get enhanced repos (runs in thread)"""
        return self.repo_stalker.stalk(username, repositories, pinned_repos)

    def __call__(self, state: AgentState) -> AgentState:
        """
        LangGraph node function
        Synchronous wrapper around async investigation
        """
        username = state["username"]
        print(f"\n{'='*60}")
        print(f"🔍 DETECTIVE AGENT CALLED")
        print(f"Username: {username}")
        print(f"{'='*60}\n")

        # Check if we already have data (for revision requests)
        if state.get("raw_data") and not state.get("revision_instructions"):
            print("🔍 THE DETECTIVE: Data already available, skipping...")
            return state

        try:
            print(f"🔧 Running async investigation in a separate thread...")

            # Run async code in a new thread with its own event loop
            def run_in_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.investigate_parallel(username))
                finally:
                    loop.close()

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_in_thread)
                raw_data = future.result()

            print(f"✅ Investigation completed successfully!")
            print(
                f"📊 Data collected: {len(raw_data.get('repositories', []))} repos")

            # Update state
            print(f"\n🔄 Updating state with detective data...")
            new_state = {
                **state,
                "raw_data": raw_data,
                "intermediate_results": {
                    **(state.get("intermediate_results") or {}),
                    "detective_completed": True,
                    "repos_analyzed": len(raw_data["repositories"]),
                },
                "messages": [
                    AIMessage(
                        content=f"✅ Successfully gathered data for @{username}. Found {len(raw_data['repositories'])} repositories."
                    )
                ],
            }
            print(f"✅ State updated, returning to graph")
            print(f"{'='*60}\n")
            return new_state

        except Exception as e:
            print(f"\n❌ DETECTIVE ERROR: {str(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            error_msg = f"Failed to fetch data for @{username}: {str(e)}"
            return {
                **state,
                "error": error_msg,
                "retry_count": state.get("retry_count", 0) + 1,
                "messages": [AIMessage(content=f"❌ {error_msg}")],
            }


# ============================================================
# AGENT 2: THE CTO (Technical Analyst)
# ============================================================

class CTOAgent:
    """
    Responsible for analyzing raw data and extracting technical insights
    Uses deterministic calculations for consistency
    """

    def __init__(self, progress_callback=None):
        self.llm = create_llm(temperature=0.3)  # Low temp for analytical tasks
        self.progress_callback = progress_callback

    def analyze(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive technical analysis
        Returns structured insights about the developer's profile
        """
        print(f"\n🧠 THE CTO: Time to judge... I mean, analyze this developer.")

        repositories = raw_data["repositories"]
        profile = raw_data["profile"]
        contributions = raw_data["contributions"]
        social_proof = raw_data["social_proof"]

        # 1. Language Analysis with Byte Dominance
        msg = "📊 Crunching language stats (bytes don't lie)..."
        print(f"  ├─ {msg}")
        if self.progress_callback:
            self.progress_callback("cto", msg)
        language_analysis = self._analyze_language_dominance(repositories)

        # 2. Skill Mapping (Libraries → Domains)
        msg = "🎯 Mapping skills to actual domains (not just buzzwords)..."
        print(f"  ├─ {msg}")
        if self.progress_callback:
            self.progress_callback("cto", msg)
        skill_mapping = self._map_skills_to_domains(repositories)

        # 3. Grind Score Calculation (EXACT FORMULA)
        msg = "💪 Calculating grind score (how hard do they really work?)..."
        print(f"  ├─ {msg}")
        if self.progress_callback:
            self.progress_callback("cto", msg)
        grind_score = self._calculate_grind_score(contributions, profile)

        # 4. Tech Diversity Assessment
        msg = "🔧 Assessing tech diversity (specialist or scattered?)..."
        print(f"  ├─ {msg}")
        if self.progress_callback:
            self.progress_callback("cto", msg)
        tech_diversity = self._assess_tech_diversity(repositories)

        # 5. Key Projects Selection (Complexity-based)
        msg = "🏆 Finding projects worth bragging about..."
        print(f"  ├─ {msg}")
        if self.progress_callback:
            self.progress_callback("cto", msg)
        key_projects = self._identify_key_projects(repositories)

        # 6. Developer Archetype
        msg = "🎭 Determining developer archetype (what's your coding personality?)..."
        print(f"  ├─ {msg}")
        if self.progress_callback:
            self.progress_callback("cto", msg)
        archetype = self._determine_archetype(
            language_analysis,
            skill_mapping,
            tech_diversity
        )

        # 7. Impact Metrics
        msg = "📈 Calculating impact (do people actually care?)..."
        print(f"  ├─ {msg}")
        if self.progress_callback:
            self.progress_callback("cto", msg)
        impact_metrics = self._calculate_impact_metrics(
            social_proof,
            contributions,
            repositories
        )

        print(
            f"  └─ ✅ Analysis complete! Verdict: {skill_mapping['personality_comment']}")

        return {
            "language_dominance": language_analysis,
            "skill_domains": skill_mapping,
            "grind_score": grind_score,
            "tech_diversity": tech_diversity,
            "key_projects": key_projects,
            "developer_archetype": archetype,
            "impact_metrics": impact_metrics,
            "summary": self._generate_summary(
                archetype,
                grind_score,
                language_analysis,
                impact_metrics
            )
        }

    def _analyze_language_dominance(self, repositories: List[Dict]) -> Dict[str, Any]:
        """
        Calculate language dominance by total bytes (not repo count)
        """
        lang_analysis = LanguageAnalyzer.analyze(repositories)

        # Get top languages sorted by percentage
        top_languages = []
        for lang, info in lang_analysis["languages"].items():
            top_languages.append({
                "name": lang,
                "percentage": info["percentage"],
                "bytes": info["size"],
                "color": info["color"]
            })

        top_languages.sort(key=lambda x: x["percentage"], reverse=True)

        # Determine primary language (>40% = dominant)
        primary = top_languages[0] if top_languages else None
        is_specialist = primary["percentage"] > 40 if primary else False

        return {
            "top_5_languages": top_languages[:5],
            "primary_language": primary,
            "is_specialist": is_specialist,
            "total_languages": lang_analysis["total_languages"],
            "language_diversity_score": min(lang_analysis["total_languages"] * 10, 100)
        }

    def _map_skills_to_domains(self, repositories: List[Dict]) -> Dict[str, Any]:
        """
        Map specific technologies to broader professional domains
        """
        skills = SkillExtractor.extract(repositories)

        # Domain mapping rules
        domain_keywords = {
            "Frontend Development": {
                "keywords": ["react", "vue", "angular", "svelte", "next.js", "nuxt", "tailwind", "bootstrap", "css", "html", "sass"],
                "frameworks": ["React", "Vue.js", "Angular", "Svelte", "Next.js"]
            },
            "Backend Development": {
                "keywords": ["django", "flask", "fastapi", "express", "nest", "spring", "laravel", "rails"],
                "frameworks": ["Django", "Flask", "FastAPI", "Express.js", "NestJS", "Spring Boot"]
            },
            "Data Science & ML": {
                "keywords": ["pandas", "numpy", "pytorch", "tensorflow", "scikit-learn", "jupyter", "matplotlib", "seaborn"],
                "frameworks": []
            },
            "DevOps & Cloud": {
                "keywords": ["docker", "kubernetes", "terraform", "ansible", "jenkins", "github-actions", "aws", "azure", "gcp"],
                "frameworks": ["Docker", "Kubernetes", "Terraform"]
            },
            "Mobile Development": {
                "keywords": ["react-native", "flutter", "expo", "swift", "kotlin", "android", "ios"],
                "frameworks": ["React Native", "Flutter", "Expo"]
            },
            "Database & Storage": {
                "keywords": ["mongodb", "postgresql", "mysql", "redis", "elasticsearch", "prisma", "typeorm"],
                "frameworks": ["MongoDB", "PostgreSQL", "Prisma"]
            },
            "Testing & QA": {
                "keywords": ["jest", "pytest", "cypress", "playwright", "selenium", "mocha", "vitest"],
                "frameworks": ["Jest", "Pytest", "Cypress"]
            },
            "Web3 & Blockchain": {
                "keywords": ["solidity", "ethereum", "web3", "blockchain", "smart-contract", "ethers", "hardhat", "truffle", "crypto", "nft", "defi"],
                "frameworks": []
            },
            "AI & Machine Learning": {
                "keywords": ["tensorflow", "pytorch", "keras", "scikit-learn", "opencv", "nlp", "deep-learning", "neural-network", "ml", "ai", "transformers", "huggingface"],
                "frameworks": ["TensorFlow", "PyTorch"]
            },
            "Data Structures & Algorithms": {
                "keywords": ["leetcode", "algorithm", "data-structure", "competitive-programming", "dsa", "sorting", "graph", "tree", "dynamic-programming"],
                "frameworks": []
            },
            "Automation & Scripting": {
                "keywords": ["automation", "script", "selenium", "puppeteer", "playwright", "bot", "scraping", "beautifulsoup", "scrapy"],
                "frameworks": []
            },
            "Game Development": {
                "keywords": ["unity", "unreal", "godot", "game", "pygame", "phaser", "three.js", "webgl", "gamedev"],
                "frameworks": ["Unity", "Unreal Engine"]
            },
            "Cybersecurity": {
                "keywords": ["security", "penetration-testing", "ethical-hacking", "cybersecurity", "ctf", "vulnerability", "encryption"],
                "frameworks": []
            }
        }

        # Calculate domain scores
        all_skills_lower = [s.lower() for s in skills["all_skills"]]
        all_frameworks = skills["frameworks"]

        domain_scores = {}
        for domain, config in domain_keywords.items():
            score = 0
            matched_techs = []

            # Check keywords
            for keyword in config["keywords"]:
                if keyword in all_skills_lower:
                    score += 1
                    matched_techs.append(keyword)

            # Check frameworks
            for framework in config["frameworks"]:
                if framework in all_frameworks:
                    score += 2  # Frameworks weigh more
                    matched_techs.append(framework)

            if score > 0:
                domain_scores[domain] = {
                    "score": score,
                    "technologies": matched_techs
                }

        # Sort domains by score
        sorted_domains = sorted(
            domain_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        # Generate personality comment
        comment = self._generate_domain_comment(sorted_domains)

        return {
            "primary_domains": [
                {"name": name, **data}
                for name, data in sorted_domains[:3]
            ],
            "all_domains": dict(sorted_domains),
            "domain_count": len(domain_scores),
            "is_full_stack": len(domain_scores) >= 3,
            "personality_comment": comment,
            # Pass through skills data
            "all_skills": skills["all_skills"],
            "frameworks": skills["frameworks"],
            "tools": skills["tools"]
        }

    def _generate_domain_comment(self, sorted_domains: List) -> str:
        """
        Generate cool/sarcastic comments based on detected domains
        """
        if not sorted_domains:
            return "Jack of all trades, master of... we're still figuring that out. 🤔"

        top_domain = sorted_domains[0][0] if sorted_domains else None
        domain_count = len(sorted_domains)

        # Specialized domain comments
        if top_domain == "Web3 & Blockchain":
            return "Riding the blockchain wave! 🌊 Either building the future or the next crypto crash. Time will tell."
        elif top_domain == "AI & Machine Learning":
            return "Teaching machines to think. Now if only we could teach them to debug... 🤖"
        elif top_domain == "Data Structures & Algorithms":
            return "LeetCode warrior spotted! Probably dreams in O(log n). 📊"
        elif top_domain == "Game Development":
            return "Making pixels dance since... well, since they started coding. 🎮"
        elif top_domain == "Cybersecurity":
            return "The digital locksmith. Breaks things professionally. 🔐"
        elif top_domain == "Automation & Scripting":
            return "Why do it yourself when you can write a script? Peak lazy = peak efficient. 🤖"
        elif top_domain == "Frontend Development":
            return "Making things pretty, one div at a time. CSS is their love language. 💅"
        elif top_domain == "Backend Development":
            return "Server-side sorcerer. Where the real magic happens (and nobody sees it). ⚙️"
        elif top_domain == "Data Science & ML":
            return "Turning data into insights. Or at least trying to. 📈"
        elif top_domain == "DevOps & Cloud":
            return "Keeps the servers running so you can keep complaining. The unsung hero. ☁️"
        elif top_domain == "Mobile Development":
            return "Building apps that you'll definitely uninstall after one use. 📱"

        # Multi-domain comments
        if domain_count >= 5:
            return "Full-stack? More like FULL-EVERYTHING. This person doesn't sleep, they just context-switch. 🎯"
        elif domain_count >= 3:
            return "Versatile af. Can't decide on one thing, so why not do them all? 🔄"
        elif domain_count == 2:
            return "The classic hybrid. Two domains, double the imposter syndrome. 💪"
        else:
            return "Laser-focused specialist. One domain to rule them all. 🎯"

    def _calculate_grind_score(self, contributions: Dict, profile: Dict) -> Dict[str, Any]:
        """
        Calculate "Grind Score" with EXACT deterministic formula

        Formula:
        - Base Score = (Total Contributions / Days Since Account Created) * 100
        - Streak Multiplier = (Current Streak / 365) * 50
        - Consistency Bonus = +20 if activity rate > 50%
        - Final Score = Base + Multiplier + Bonus

        Labels:
        - <20 = Casual
        - 20-40 = Active
        - 40-60 = Consistent
        - 60+ = Grinder
        """
        contrib_calendar = ContributionCalendar.analyze(contributions)

        # Calculate days since account creation
        from datetime import datetime
        created_at = datetime.fromisoformat(
            profile["created_at"].replace("Z", "+00:00"))
        days_since_creation = (datetime.now(
            created_at.tzinfo) - created_at).days

        # Avoid division by zero
        if days_since_creation == 0:
            days_since_creation = 1

        # Base score
        base_score = (
            contrib_calendar["total_contributions"] / days_since_creation) * 100

        # Streak multiplier
        streak_multiplier = (contrib_calendar["current_streak"] / 365) * 50

        # Consistency bonus
        consistency_bonus = 20 if contrib_calendar["activity_rate"] > 50 else 0

        # Final score
        final_score = base_score + streak_multiplier + consistency_bonus

        # Determine label
        if final_score < 20:
            label = "Casual"
            emoji = "🌱"
        elif final_score < 40:
            label = "Active"
            emoji = "🔥"
        elif final_score < 60:
            label = "Consistent"
            emoji = "💪"
        else:
            label = "Grinder"
            emoji = "🚀"

        return {
            "score": round(final_score, 2),
            "label": label,
            "emoji": emoji,
            "breakdown": {
                "base_score": round(base_score, 2),
                "streak_multiplier": round(streak_multiplier, 2),
                "consistency_bonus": consistency_bonus
            },
            "contributing_factors": {
                "total_contributions": contrib_calendar["total_contributions"],
                "current_streak": contrib_calendar["current_streak"],
                "longest_streak": contrib_calendar["longest_streak"],
                "activity_rate": contrib_calendar["activity_rate"],
                "days_since_creation": days_since_creation
            }
        }

    def _assess_tech_diversity(self, repositories: List[Dict]) -> Dict[str, Any]:
        """
        Assess if developer is a "One-Trick Pony" or "Full Stack Generalist"
        """
        # Collect all detected technologies
        all_tech = set()
        tech_frequency = {}

        for repo in repositories:
            for tech in repo.get("detected_tech_stack", []):
                all_tech.add(tech)
                tech_frequency[tech] = tech_frequency.get(tech, 0) + 1

        # Count unique tech categories
        categories = {
            "languages": set(),
            "frameworks": set(),
            "databases": set(),
            "devops": set(),
            "testing": set()
        }

        language_keywords = ["Python", "JavaScript",
                             "TypeScript", "Java", "Go", "Rust", "C++"]
        framework_keywords = ["React", "Vue.js", "Angular",
                              "Django", "Flask", "Express.js", "Next.js"]
        database_keywords = ["MongoDB",
                             "PostgreSQL", "MySQL", "Redis", "Prisma"]
        devops_keywords = ["Docker", "Kubernetes",
                           "Terraform", "GitHub Actions"]
        testing_keywords = ["Jest", "Pytest", "Cypress", "Playwright"]

        for tech in all_tech:
            if tech in language_keywords:
                categories["languages"].add(tech)
            if tech in framework_keywords:
                categories["frameworks"].add(tech)
            if tech in database_keywords:
                categories["databases"].add(tech)
            if tech in devops_keywords:
                categories["devops"].add(tech)
            if tech in testing_keywords:
                categories["testing"].add(tech)

        # Calculate diversity score
        diversity_score = (
            len(categories["languages"]) * 10 +
            len(categories["frameworks"]) * 8 +
            len(categories["databases"]) * 6 +
            len(categories["devops"]) * 5 +
            len(categories["testing"]) * 4
        )

        # Determine classification
        if diversity_score < 30:
            classification = "Specialist"
            description = "Focused expertise in specific technologies"
        elif diversity_score < 60:
            classification = "Versatile Developer"
            description = "Comfortable across multiple domains"
        else:
            classification = "Full Stack Generalist"
            description = "Broad expertise across the entire stack"

        return {
            "total_technologies": len(all_tech),
            "diversity_score": diversity_score,
            "classification": classification,
            "description": description,
            "category_breakdown": {
                "languages": len(categories["languages"]),
                "frameworks": len(categories["frameworks"]),
                "databases": len(categories["databases"]),
                "devops": len(categories["devops"]),
                "testing": len(categories["testing"])
            },
            "most_used_technologies": sorted(
                tech_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

    def _identify_key_projects(self, repositories: List[Dict]) -> List[Dict]:
        """
        Select 3 most impressive projects based on complexity (not just stars)

        Complexity Score = Stars * 2 + Forks * 3 + Tech Diversity * 5 + (Has README) * 10
        """
        scored_repos = []

        for repo in repositories:
            if repo.get("is_fork") or repo.get("is_archived"):
                continue  # Skip forks and archived repos

            complexity_score = (
                repo.get("stars", 0) * 2 +
                repo.get("forks", 0) * 3 +
                len(repo.get("detected_tech_stack", [])) * 5 +
                (10 if repo.get("readme_content") else 0)
            )

            scored_repos.append({
                "name": repo["name"],
                "description": repo["description"],
                "url": repo["url"],
                "stars": repo["stars"],
                "forks": repo["forks"],
                "primary_language": repo["primary_language"],
                "tech_stack": repo.get("detected_tech_stack", []),
                "complexity_score": complexity_score,
                "is_pinned": repo.get("is_pinned", False)
            })

        # Sort by complexity score
        scored_repos.sort(key=lambda x: x["complexity_score"], reverse=True)

        return scored_repos[:3]

    def _determine_archetype(
        self,
        language_analysis: Dict,
        skill_domains: Dict,
        tech_diversity: Dict
    ) -> Dict[str, Any]:
        """
        Determine developer archetype based on analysis
        """
        primary_lang = language_analysis["primary_language"]
        is_specialist = language_analysis["is_specialist"]
        primary_domains = skill_domains["primary_domains"]
        diversity_class = tech_diversity["classification"]

        # Determine archetype
        if is_specialist and primary_domains:
            domain_name = primary_domains[0]["name"]
            archetype = f"{primary_lang['name']} {domain_name} Specialist"
        elif len(primary_domains) >= 2:
            archetype = "Full Stack Developer"
        elif primary_lang:
            archetype = f"{primary_lang['name']} Developer"
        else:
            archetype = "Software Engineer"

        # Add secondary descriptor
        if tech_diversity["diversity_score"] > 60:
            secondary = "Polyglot"
        elif tech_diversity["total_technologies"] > 20:
            secondary = "Tech Explorer"
        else:
            secondary = "Focused Engineer"

        return {
            "primary": archetype,
            "secondary": secondary,
            "full_title": f"{archetype} | {secondary}",
            "confidence": "high" if is_specialist else "medium"
        }

    def _calculate_impact_metrics(
        self,
        social_proof: Dict,
        contributions: Dict,
        repositories: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate impact metrics for the developer
        """
        contrib_calendar = ContributionCalendar.analyze(contributions)

        # Calculate engagement rate
        repos_with_stars = sum(
            1 for r in repositories if r.get("stars", 0) > 0)
        engagement_rate = (repos_with_stars / len(repositories)
                           * 100) if repositories else 0

        # Calculate contribution intensity
        contribution_intensity = contrib_calendar["average_daily"]

        return {
            "total_stars": social_proof["total_stars"],
            "total_forks": social_proof["total_forks"],
            "total_followers": social_proof["total_followers"],
            "engagement_rate": round(engagement_rate, 2),
            "contribution_intensity": contribution_intensity,
            "impact_score": round(
                (social_proof["total_stars"] * 0.5 +
                 social_proof["total_forks"] * 1.5 +
                 social_proof["total_followers"] * 2) / 10,
                2
            )
        }

    def _generate_summary(
        self,
        archetype: Dict,
        grind_score: Dict,
        language_analysis: Dict,
        impact_metrics: Dict
    ) -> str:
        """
        Generate a human-readable summary
        """
        primary_lang = language_analysis["primary_language"]
        lang_name = primary_lang["name"] if primary_lang else "multiple languages"

        summary = f"{archetype['full_title']} with {grind_score['emoji']} {grind_score['label']} activity. "
        summary += f"Primary expertise in {lang_name} "
        summary += f"with {impact_metrics['total_stars']} total stars across projects."

        return summary

    def __call__(self, state: AgentState) -> AgentState:
        """
        LangGraph node function
        """
        # Check if we already have analysis (for revision requests)
        if state.get("analysis") and not state.get("revision_instructions"):
            print("🧠 THE CTO: Analysis already available, skipping...")
            return state

        # Ensure we have raw data
        if not state.get("raw_data"):
            error_msg = "Cannot analyze without raw data. Detective must run first."
            return {
                **state,
                "error": error_msg,
                "messages": [AIMessage(content=f"❌ {error_msg}")],
            }

        try:
            # Perform analysis
            analysis = self.analyze(state["raw_data"])

            # Update state
            return {
                **state,
                "analysis": analysis,
                "intermediate_results": {
                    **(state.get("intermediate_results") or {}),
                    "cto_completed": True,
                    "grind_score": analysis["grind_score"]["score"],
                    "archetype": analysis["developer_archetype"]["full_title"],
                },
                "messages": [
                    AIMessage(
                        content=f"✅ Analysis complete: {analysis['summary']}"
                    )
                ],
            }

        except Exception as e:
            error_msg = f"Failed to analyze data: {str(e)}"
            return {
                **state,
                "error": error_msg,
                "messages": [AIMessage(content=f"❌ {error_msg}")],
            }


# ============================================================
# GHOSTWRITER AGENT - The Creative Director
# ============================================================

class GhostwriterAgent:
    """
    The Ghostwriter - Generates beautiful, engaging GitHub README files
    Supports multiple tones: Professional, GenZ, Minimalist
    Uses shields.io badges, github-readme-stats, and creative flair
    """

    def __init__(self):
        """Initialize Ghostwriter with LLM for creative generation"""
        if not GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables")

        # Higher temperature for creative writing
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            google_api_key=GOOGLE_API_KEY,
        )

    def __call__(self, state: AgentState) -> AgentState:
        """
        Generate markdown README from Detective's data + CTO's analysis
        """
        print("\n" + "=" * 70)
        print("✍️  GHOSTWRITER AGENT - Crafting Your Digital Masterpiece...")
        print("=" * 70)

        try:
            username = state["username"]
            raw_data = state.get("raw_data")
            analysis = state.get("analysis")
            preferences = state.get("user_preferences", {})
            revision_instructions = state.get("revision_instructions")

            if not raw_data or not analysis:
                return {
                    **state,
                    "error": "Missing data or analysis. Run Detective and CTO first.",
                    "messages": [AIMessage(content="❌ Need data before I can write!")],
                }

            print(
                f"  ├─ 🎨 Tone: {preferences.get('tone', 'professional').title()}")
            print(
                f"  ├─ 📝 Style: {preferences.get('style', 'modern').title()}")

            if revision_instructions:
                print(f"  ├─ 🔄 Revision Request: {revision_instructions}")

            # Generate the README markdown
            markdown = self._generate_markdown(
                username=username,
                raw_data=raw_data,
                analysis=analysis,
                preferences=preferences,
                revision_instructions=revision_instructions
            )

            # Add personality comment
            comment = self._generate_writing_comment(
                analysis, preferences.get("tone"))
            print(f"\n  └─ 💬 {comment}")

            # Update generation history
            history = state.get("generation_history", [])
            history.append({
                "version": len(history) + 1,
                "markdown": markdown,
                "preferences": preferences.copy(),
                "revision_instructions": revision_instructions
            })

            print("\n✅ README Generated Successfully!")
            print(f"   - Length: {len(markdown)} characters")
            print(f"   - Lines: {len(markdown.split(chr(10)))}")
            print(f"   - Version: {len(history)}")

            return {
                **state,
                "final_markdown": markdown,
                "generation_history": history,
                "revision_instructions": None,  # Clear after processing
                "intermediate_results": {
                    **(state.get("intermediate_results") or {}),
                    "ghostwriter_completed": True,
                    "markdown_length": len(markdown),
                    "version": len(history),
                },
                "messages": [
                    AIMessage(
                        content=f"✅ README generated! ({len(markdown)} chars, v{len(history)})")
                ],
            }

        except Exception as e:
            error_msg = f"Failed to generate README: {str(e)}"
            print(f"\n❌ {error_msg}")
            return {
                **state,
                "error": error_msg,
                "messages": [AIMessage(content=f"❌ {error_msg}")],
            }

    def _generate_markdown(
        self,
        username: str,
        raw_data: Dict[str, Any],
        analysis: Dict[str, Any],
        preferences: Dict[str, Any],
        revision_instructions: Optional[str] = None
    ) -> str:
        """
        Generate the actual markdown content
        Uses LLM for intelligent content generation with provided data
        """
        tone = preferences.get("tone", "professional")
        style = preferences.get("style", "modern")

        # Extract key data
        profile = raw_data["profile"]
        repos = raw_data["repositories"]
        social_proof = raw_data["social_proof"]
        archetype = analysis["developer_archetype"]
        grind_score = analysis["grind_score"]
        tech_diversity = analysis["tech_diversity"]
        primary_lang = analysis["language_dominance"]["primary_language"]
        key_projects = analysis["key_projects"]

        # Build system prompt based on tone
        tone_instructions = self._get_tone_instructions(tone)

        system_prompt = f"""You are an expert README writer creating a GitHub profile README for {username}.

{tone_instructions}

CRITICAL RULES:
1. Use REAL data provided - NO placeholders or made-up content
2. Include shields.io badges for top languages/frameworks
3. Add github-readme-stats with username: {username}
4. Highlight top {len(key_projects)} projects with descriptions
5. Show personality through {tone} tone
6. Use emojis strategically (not overdone)
7. Include social proof (stars: {social_proof['total_stars']}, followers: {profile.get('followers', 0)})
8. Make it visually appealing with proper markdown formatting

STRUCTURE:
- Header with name and tagline (based on archetype: {archetype['full_title']})
- About section (bio + grind score: {grind_score['label']})
- Tech Stack section (primary: {primary_lang['name']}, diversity: {tech_diversity['classification']})
- Featured Projects (top {len(key_projects)} repos)
- GitHub Stats (badges + readme-stats)
- Connect section (if public data available)

"""

        if revision_instructions:
            system_prompt += f"\n\nREVISION REQUEST: {revision_instructions}\nApply this change while keeping all other sections intact."

        # Build data summary for LLM
        data_summary = f"""
USER DATA:
- Username: {username}
- Name: {profile.get('name', username)}
- Bio: {profile.get('bio', 'No bio available')}
- Location: {profile.get('location', 'Unknown')}
- Company: {profile.get('company', 'N/A')}
- Followers: {profile.get('followers', 0)}
- Following: {profile.get('following', 0)}
- Public Repos: {profile.get('public_repos', 0)}
- Created: {profile.get('created_at', 'N/A')}

DEVELOPER ARCHETYPE:
- Title: {archetype['full_title']}
- Primary: {archetype['primary']}
- Secondary: {archetype['secondary']}
- Confidence: {archetype['confidence']}

GRIND SCORE:
- Score: {grind_score['score']}
- Label: {grind_score['label']}
- Emoji: {grind_score['emoji']}

SOCIAL PROOF:
- Total Stars: {social_proof['total_stars']}
- Total Forks: {social_proof['total_forks']}
- Average Stars: {social_proof['average_stars_per_repo']}
- Most Starred: {social_proof['most_starred_repo']['name']} ({social_proof['most_starred_repo']['stars']} ⭐)

TECH STACK:
- Primary Language: {primary_lang['name']} ({primary_lang['percentage']}%)
- Total Languages: {analysis['language_dominance']['total_languages']}
- Tech Diversity: {tech_diversity['classification']}
- All Skills: {', '.join(analysis['skill_domains']['all_skills'][:20])}

TOP PROJECTS:
"""
        for i, project in enumerate(key_projects[:5], 1):
            data_summary += f"\n{i}. {project['name']} ({project['stars']} ⭐, {project['forks']} 🍴)"
            data_summary += f"\n   - Description: {project.get('description', 'No description')}"
            data_summary += f"\n   - Languages: {', '.join(project.get('languages', ['Unknown']))}"
            data_summary += f"\n   - URL: https://github.com/{username}/{project['name']}"

        # Generate with LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=data_summary +
                         "\n\nGenerate a complete, beautiful GitHub README.md in markdown format.")
        ]

        response = self.llm.invoke(messages)
        markdown = response.content

        # Post-process: ensure it has proper structure
        markdown = self._post_process_markdown(
            markdown, username, primary_lang['name'])

        return markdown

    def _get_tone_instructions(self, tone: str) -> str:
        """Get writing instructions based on tone"""
        instructions = {
            "professional": """
TONE: Professional and polished
- Clear, concise, business-appropriate language
- Highlight achievements and technical expertise
- Use industry-standard terminology
- Maintain credibility and authority
""",
            "genz": """
TONE: GenZ vibes - casual, relatable, internet-native
- Use modern slang (lowkey, ngl, fr, no cap) but keep it readable
- Conversational and authentic
- Self-aware humor and light sarcasm
- Emojis used naturally (not forced)
- Short, punchy sentences
""",
            "minimalist": """
TONE: Minimalist and clean
- Ultra-concise, no fluff
- Focus on data and facts
- Minimal emojis (only when highly relevant)
- Clean structure with plenty of whitespace
- Let the work speak for itself
""",
            "creative": """
TONE: Creative and unique
- Storytelling elements
- Unique metaphors and descriptions
- Personality shines through
- Balance creativity with professionalism
""",
        }
        return instructions.get(tone, instructions["professional"])

    def _post_process_markdown(self, markdown: str, username: str, primary_lang: str) -> str:
        """
        Post-process generated markdown to ensure quality
        Add missing elements if needed
        """
        # Ensure github-readme-stats is included
        if "github-readme-stats" not in markdown:
            stats_section = f"""
## 📊 GitHub Stats

![{username}'s GitHub Stats](https://github-readme-stats.vercel.app/api?username={username}&show_icons=true&theme=radical)

![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username={username}&layout=compact&theme=radical)
"""
            markdown += "\n" + stats_section

        # Ensure shields.io badge for primary language
        if "shields.io" not in markdown and primary_lang:
            badge = f"![{primary_lang}](https://img.shields.io/badge/-{primary_lang}-blue?style=flat-square&logo={primary_lang.lower()})"
            # Try to add after header
            lines = markdown.split("\n")
            if len(lines) > 2:
                lines.insert(2, f"\n{badge}\n")
                markdown = "\n".join(lines)

        return markdown.strip()

    def _generate_writing_comment(self, analysis: Dict[str, Any], tone: Optional[str]) -> str:
        """Generate a personality comment about the writing process"""
        archetype = analysis["developer_archetype"]["primary"]
        grind_level = analysis["grind_score"]["label"]

        # Simple tone-based comments (archetype is too varied to match)
        tone_key = tone or "professional"

        comments = {
            "professional": "📝 Crafted a polished, professional profile that stands out!",
            "genz": "✍️ Just wrote your digital flex - this README hits different fr fr!",
            "minimalist": "📄 Clean, concise, and to the point - exactly how it should be!",
            "creative": "🎨 Crafted a unique profile that showcases your personality!",
        }

        base_comment = comments.get(
            tone_key, "✨ Your profile is now ready to shine!")

        # Add grind score flavor
        if grind_level == "🔥 Absolute Legend":
            base_comment += " (Your stats are literally insane btw)"
        elif grind_level == "💪 Solid Grinder":
            base_comment += " (Respectable grind detected)"

        return base_comment


# ============================================================
# ROUTING LOGIC (No LLM - Deterministic)
# ============================================================

def route_next_step(state: AgentState) -> str:
    """
    Deterministic routing based on state
    No LLM needed - fast and reliable
    """
    # Error handling - give up after retries
    if state.get("error"):
        retry_count = state.get("retry_count", 0)
        if retry_count >= 3:
            return END  # Give up after 3 retries

        # Only retry detective if we don't have raw data yet
        if state.get("raw_data") is None:
            return "detective"
        # Only retry CTO if we don't have analysis yet
        elif state.get("analysis") is None:
            return "cto"
        # If we have data and analysis, ghostwriter error should end
        else:
            return END

    # Check if this is a revision request
    if state.get("revision_instructions"):
        # Skip to ghostwriter with revision context
        return "ghostwriter"

    # Normal flow: Detective → CTO → Ghostwriter → END
    if state.get("raw_data") is None:
        return "detective"
    elif state.get("analysis") is None:
        return "cto"
    elif state.get("final_markdown") is None:
        return "ghostwriter"
    else:
        return END


# ============================================================
# GRAPH BUILDER
# ============================================================

def create_detective_graph(progress_callback=None) -> StateGraph:
    """
    Create the complete LangGraph with Detective, CTO, and Ghostwriter agents
    Full pipeline: Data Collection → Analysis → README Generation
    """
    # Initialize memory for checkpointing
    memory = MemorySaver()

    # Create graph
    workflow = StateGraph(AgentState)

    # Initialize agents
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_PAT not found in environment variables")

    detective = DetectiveAgent(
        GITHUB_TOKEN, progress_callback=progress_callback)
    cto = CTOAgent(progress_callback=progress_callback)
    ghostwriter = GhostwriterAgent()

    # Add nodes
    workflow.add_node("detective", detective)
    workflow.add_node("cto", cto)
    workflow.add_node("ghostwriter", ghostwriter)

    # Add conditional routing (deterministic - no LLM)
    workflow.set_conditional_entry_point(
        route_next_step,
        {
            "detective": "detective",
            "cto": "cto",
            "ghostwriter": "ghostwriter",
            END: END,
        }
    )

    workflow.add_conditional_edges(
        "detective",
        route_next_step,
        {
            "detective": "detective",  # Retry on error
            "cto": "cto",  # Normal flow
            END: END,
        }
    )

    workflow.add_conditional_edges(
        "cto",
        route_next_step,
        {
            "ghostwriter": "ghostwriter",  # Flow to Ghostwriter
            END: END,
        }
    )

    workflow.add_conditional_edges(
        "ghostwriter",
        route_next_step,
        {
            "ghostwriter": "ghostwriter",  # Allow revisions
            "detective": "detective",  # Retry on error
            "cto": "cto",  # Fallback if analysis missing
            END: END,
        }
    )

    # Compile with checkpointing
    return workflow.compile(checkpointer=memory)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_initial_state(username: str, preferences: Optional[Dict] = None) -> AgentState:
    """Create initial state for the agent"""
    return {
        "username": username,
        "user_preferences": preferences or {"tone": "professional", "style": "modern"},
        "raw_data": None,
        "analysis": None,
        "final_markdown": None,
        "messages": [HumanMessage(content=f"Generate a GitHub README for @{username}")],
        "error": None,
        "retry_count": 0,
        "intermediate_results": {},
        "revision_instructions": None,
        "generation_history": [],
    }


# ============================================================
# MAIN (For Testing)
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 GRWM - Agentic System (Detective + CTO + Ghostwriter)")
    print("=" * 70)

    # Create the graph
    app = create_detective_graph()

    # Test with a username
    test_username = input(
        "\n👤 Enter GitHub username to test: ").strip()

    if not test_username:
        print("❌ Username required")
    else:
        # Get preferences
        print("\n🎨 README Preferences:")
        print("1. Professional (polished, business-ready)")
        print("2. GenZ (casual, relatable vibes)")
        print("3. Minimalist (clean, data-focused)")
        print("4. Creative (unique, storytelling)")

        tone_choice = input("Select tone (1-4, default=1): ").strip()
        tone_map = {"1": "professional", "2": "genz",
                    "3": "minimalist", "4": "creative"}
        tone = tone_map.get(tone_choice, "professional")

        # Create initial state
        initial_state = create_initial_state(
            test_username,
            preferences={"tone": tone, "style": "modern"}
        )

        # Run the graph
        print(f"\n{'=' * 70}")
        print("🤖 Running Complete Agent Pipeline...")
        print(f"{'=' * 70}")

        try:
            # Execute with streaming (need thread_id for checkpointer)
            config = {
                "configurable": {"thread_id": f"test_{test_username}"},
                "recursion_limit": 15
            }

            for event in app.stream(initial_state, config):
                print(f"\n📡 Event: {list(event.keys())}")

                # Check Detective
                if "detective" in event:
                    agent_state = event["detective"]
                    if agent_state.get("error"):
                        print(f"❌ Detective Error: {agent_state['error']}")
                    elif agent_state.get("raw_data"):
                        print(f"✅ Detective completed successfully!")
                        print(
                            f"   - Repositories: {len(agent_state['raw_data']['repositories'])}")
                        print(
                            f"   - Total Stars: {agent_state['raw_data']['social_proof']['total_stars']}")

                # Check CTO
                if "cto" in event:
                    agent_state = event["cto"]
                    if agent_state.get("error"):
                        print(f"❌ CTO Error: {agent_state['error']}")
                    elif agent_state.get("analysis"):
                        analysis = agent_state["analysis"]
                        print(f"✅ CTO completed successfully!")
                        print(
                            f"   - Archetype: {analysis['developer_archetype']['full_title']}")
                        print(
                            f"   - Grind Score: {analysis['grind_score']['score']} ({analysis['grind_score']['label']} {analysis['grind_score']['emoji']})")
                        print(
                            f"   - Primary Language: {analysis['language_dominance']['primary_language']['name']} ({analysis['language_dominance']['primary_language']['percentage']}%)")
                        print(
                            f"   - Tech Diversity: {analysis['tech_diversity']['classification']}")
                        print(
                            f"   - Key Projects: {len(analysis['key_projects'])}")

                # Check Ghostwriter
                if "ghostwriter" in event:
                    agent_state = event["ghostwriter"]
                    if agent_state.get("error"):
                        print(f"❌ Ghostwriter Error: {agent_state['error']}")
                    elif agent_state.get("final_markdown"):
                        markdown = agent_state["final_markdown"]
                        print(f"✅ Ghostwriter completed successfully!")
                        print(
                            f"   - Markdown Length: {len(markdown)} characters")
                        print(f"   - Lines: {len(markdown.split(chr(10)))}")
                        print(
                            f"   - Version: {len(agent_state.get('generation_history', []))}")

            print("\n" + "=" * 70)
            print("✨ Complete Agent Pipeline Finished!")
            print("=" * 70)

            # Ask if user wants to see the README
            show_readme = input(
                "\n📄 Show generated README? (y/n): ").strip().lower()
            if show_readme == 'y':
                # Get final state
                final_state = app.get_state(config)
                if final_state.values.get("final_markdown"):
                    print("\n" + "=" * 70)
                    print("📝 GENERATED README.md")
                    print("=" * 70 + "\n")
                    print(final_state.values["final_markdown"])
                    print("\n" + "=" * 70)

                    # Ask to save
                    save = input("\n💾 Save to file? (y/n): ").strip().lower()
                    if save == 'y':
                        filename = f"README_{test_username}.md"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(final_state.values["final_markdown"])
                        print(f"✅ Saved to {filename}")

        except Exception as e:
            print(f"\n❌ Error running agent: {e}")
            import traceback
            traceback.print_exc()
