"""
GRWM - GitHub README With Me
Agentic AI system to generate awesome GitHub profile READMEs
"""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from collections import Counter

# Load environment variables
load_dotenv()

GITHUB_API_URL = "https://api.github.com/graphql"
GITHUB_TOKEN = os.getenv("GITHUB_PAT")


class GitHubAPIClient:
    """Base client for GitHub GraphQL API interactions"""

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute a GraphQL query"""
        response = requests.post(
            GITHUB_API_URL,
            json={"query": query, "variables": variables or {}},
            headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(
                f"Query failed: {response.status_code} - {response.text}")

        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")

        return result["data"]


class ProfileDetective:
    """Fetch comprehensive user profile details from GitHub"""

    def __init__(self, client: GitHubAPIClient):
        self.client = client

    def investigate(self, username: str) -> Dict[str, Any]:
        """
        Fetch all profile details in a SINGLE optimized query
        Returns: name, bio, company, location, avatar, social links, 
                 contribution history, repos, pinned repos, followers/following, etc.
        """
        query = """
        query($username: String!) {
          user(login: $username) {
            name
            login
            bio
            company
            location
            email
            websiteUrl
            twitterUsername
            avatarUrl
            createdAt
            isHireable
            status {
              emoji
              message
            }
            followers {
              totalCount
            }
            following {
              totalCount
            }
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    contributionCount
                    date
                  }
                }
              }
              totalCommitContributions
              totalIssueContributions
              totalPullRequestContributions
              totalPullRequestReviewContributions
              restrictedContributionsCount
            }
            repositories(
              first: 100
              orderBy: {field: STARGAZERS, direction: DESC}
              ownerAffiliations: OWNER
              privacy: PUBLIC
            ) {
              totalCount
              nodes {
                name
                description
                url
                stargazerCount
                forkCount
                primaryLanguage {
                  name
                  color
                }
                languages(first: 10) {
                  edges {
                    size
                    node {
                      name
                      color
                    }
                  }
                }
                repositoryTopics(first: 10) {
                  nodes {
                    topic {
                      name
                    }
                  }
                }
                createdAt
                updatedAt
                isPrivate
                isFork
                isArchived
                licenseInfo {
                  name
                }
              }
            }
            pinnedItems(first: 6, types: REPOSITORY) {
              nodes {
                ... on Repository {
                  name
                  description
                  url
                  stargazerCount
                  forkCount
                  primaryLanguage {
                    name
                    color
                  }
                }
              }
            }
            topRepositories(
              first: 10
              orderBy: {field: STARGAZERS, direction: DESC}
            ) {
              nodes {
                name
                stargazerCount
              }
            }
            socialAccounts(first: 10) {
              edges {
                node {
                  provider
                  url
                  displayName
                }
              }
            }
          }
        }
        """

        data = self.client.execute_query(query, {"username": username})
        user = data["user"]

        # Process and structure the data
        profile = {
            "basic_info": {
                "name": user["name"],
                "username": user["login"],
                "bio": user["bio"],
                "company": user["company"],
                "location": user["location"],
                "email": user["email"],
                "website": user["websiteUrl"],
                "twitter": user["twitterUsername"],
                "avatar_url": user["avatarUrl"],
                "created_at": user["createdAt"],
                "is_hireable": user["isHireable"],
                "status": user["status"]
            },
            "stats": {
                "followers": user["followers"]["totalCount"],
                "following": user["following"]["totalCount"],
                "total_repos": user["repositories"]["totalCount"],
            },
            "contributions": {
                "total": user["contributionsCollection"]["contributionCalendar"]["totalContributions"],
                "commits": user["contributionsCollection"]["totalCommitContributions"],
                "issues": user["contributionsCollection"]["totalIssueContributions"],
                "pull_requests": user["contributionsCollection"]["totalPullRequestContributions"],
                "code_reviews": user["contributionsCollection"]["totalPullRequestReviewContributions"],
                "calendar": user["contributionsCollection"]["contributionCalendar"]["weeks"]
            },
            "repositories": user["repositories"]["nodes"],
            "pinned_repos": [repo for repo in user["pinnedItems"]["nodes"]],
            "top_starred_repos": user["topRepositories"]["nodes"],
            "social_accounts": [
                {
                    "provider": edge["node"]["provider"],
                    "url": edge["node"]["url"],
                    "display_name": edge["node"]["displayName"]
                }
                for edge in user["socialAccounts"]["edges"]
            ]
        }

        return profile


class RepositoryStalker:
    """Deep dive into repository details with intelligent prioritization"""

    def __init__(self, client: GitHubAPIClient):
        self.client = client

    def stalk(self, username: str, repositories: List[Dict], pinned_repos: List[Dict], max_repos: int = 15) -> List[Dict]:
        """
        Analyze repositories with smart prioritization:
        1. All pinned repos (up to 6)
        2. Top starred repos
        3. Recently active repos
        Total: EXACTLY 15 unique repos
        """
        # Get pinned repo names for quick lookup
        pinned_names = {repo["name"] for repo in pinned_repos}

        # Create a set to track unique repo names
        seen_repos = set()
        selected_repos = []

        # First, add all pinned repos (up to 6 unique)
        for repo in repositories:
            if repo["name"] in pinned_names and repo["name"] not in seen_repos:
                selected_repos.append(repo)
                seen_repos.add(repo["name"])
                if len(selected_repos) >= 6:
                    break

        # If we already have 15 unique repos, stop
        if len(selected_repos) >= max_repos:
            selected_repos = selected_repos[:max_repos]
        else:
            # Sort non-pinned by stars and recency for remaining slots
            non_pinned_sorted = sorted(
                repositories,
                key=lambda x: (x["stargazerCount"], x["updatedAt"]),
                reverse=True
            )

            # Add remaining repos until we hit 15 unique
            for repo in non_pinned_sorted:
                if repo["name"] not in seen_repos:
                    selected_repos.append(repo)
                    seen_repos.add(repo["name"])
                    if len(selected_repos) >= max_repos:
                        break

        # Ensure exactly 15 repos (or less if user has fewer repos)
        final_repos = selected_repos[:max_repos]

        # Enhance with detailed stats
        enhanced_repos = []
        for repo in final_repos:
            enhanced = {
                "name": repo["name"],
                "description": repo["description"],
                "url": repo["url"],
                "stars": repo["stargazerCount"],
                "forks": repo["forkCount"],
                "primary_language": repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else None,
                "languages": [
                    {
                        "name": edge["node"]["name"],
                        "size": edge["size"],
                        "color": edge["node"]["color"]
                    }
                    for edge in repo["languages"]["edges"]
                ],
                "topics": [
                    node["topic"]["name"]
                    for node in repo["repositoryTopics"]["nodes"]
                ],
                "created_at": repo["createdAt"],
                "updated_at": repo["updatedAt"],
                "is_fork": repo["isFork"],
                "is_archived": repo["isArchived"],
                "license": repo["licenseInfo"]["name"] if repo["licenseInfo"] else None,
                "is_pinned": repo["name"] in pinned_names
            }
            enhanced_repos.append(enhanced)

        return enhanced_repos


class ExReadme:
    """Fetch existing README from user's profile repository"""

    def __init__(self, client: GitHubAPIClient):
        self.client = client

    def read(self, username: str) -> Optional[str]:
        """
        Fetch existing README.md from username/username repository
        Returns None if not found
        """
        query = """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            object(expression: "HEAD:README.md") {
              ... on Blob {
                text
              }
            }
          }
        }
        """

        try:
            data = self.client.execute_query(
                query,
                {"owner": username, "name": username}
            )

            if data["repository"] and data["repository"]["object"]:
                return data["repository"]["object"]["text"]
            return None
        except Exception as e:
            print(f"Could not fetch existing README: {e}")
            return None


class TechStackDetective:
    """Detect tech stack from repository file structure and extract README content"""

    # Comprehensive tech stack patterns
    TECH_PATTERNS = {
        # Frontend Frameworks & Libraries
        "React": ["package.json:react", ".jsx", ".tsx"],
        "Next.js": ["next.config.js", "next.config.ts", "next.config.mjs"],
        "Vue.js": ["package.json:vue", ".vue", "vue.config.js"],
        "Nuxt.js": ["nuxt.config.js", "nuxt.config.ts"],
        "Angular": ["angular.json", "package.json:@angular"],
        "Svelte": ["svelte.config.js", "package.json:svelte"],
        "SvelteKit": ["svelte.config.js:@sveltejs/kit"],

        # CSS Frameworks & Preprocessors
        "Tailwind CSS": ["tailwind.config.js", "tailwind.config.ts", "tailwind.config.cjs"],
        "Bootstrap": ["package.json:bootstrap", ".scss:bootstrap"],
        "Material-UI": ["package.json:@mui", "package.json:@material-ui"],
        "Sass/SCSS": [".scss", ".sass", "sass.config.js"],
        "Less": [".less", "less.config.js"],
        "PostCSS": ["postcss.config.js", "postcss.config.cjs"],

        # Backend Frameworks
        "Express.js": ["package.json:express"],
        "Fastify": ["package.json:fastify"],
        "NestJS": ["nest-cli.json", "package.json:@nestjs"],
        "Django": ["manage.py", "settings.py", "requirements.txt:django"],
        "Flask": ["app.py:Flask", "requirements.txt:flask"],
        "FastAPI": ["main.py:fastapi", "requirements.txt:fastapi"],
        "Spring Boot": ["pom.xml:spring-boot", "build.gradle:spring-boot"],
        "Ruby on Rails": ["Gemfile:rails", "config/routes.rb"],
        "Laravel": ["composer.json:laravel", "artisan"],

        # Databases & ORMs
        "MongoDB": ["package.json:mongodb", "package.json:mongoose"],
        "PostgreSQL": ["package.json:pg", "requirements.txt:psycopg2"],
        "MySQL": ["package.json:mysql", "requirements.txt:mysql"],
        "SQLite": [".sqlite", ".db", "requirements.txt:sqlite"],
        "Redis": ["package.json:redis", "requirements.txt:redis"],
        "Prisma": ["prisma/schema.prisma", "package.json:@prisma"],
        "TypeORM": ["package.json:typeorm"],
        "Sequelize": ["package.json:sequelize"],

        # Build Tools & Bundlers
        "Webpack": ["webpack.config.js", "webpack.config.ts"],
        "Vite": ["vite.config.js", "vite.config.ts"],
        "Rollup": ["rollup.config.js"],
        "Parcel": [".parcelrc", "package.json:parcel"],
        "esbuild": ["package.json:esbuild"],
        "Turbopack": ["package.json:turbopack"],

        # Testing Frameworks
        "Jest": ["jest.config.js", "package.json:jest"],
        "Vitest": ["vitest.config.js", "package.json:vitest"],
        "Pytest": ["pytest.ini", "requirements.txt:pytest"],
        "Mocha": ["package.json:mocha"],
        "Cypress": ["cypress.json", "cypress.config.js"],
        "Playwright": ["playwright.config.js", "package.json:playwright"],

        # DevOps & Containers
        "Docker": ["Dockerfile", "docker-compose.yml", ".dockerignore"],
        "Kubernetes": ["deployment.yaml", "k8s/", "kustomization.yaml"],
        "Terraform": [".tf", "terraform.tfvars"],
        "GitHub Actions": [".github/workflows/"],
        "CircleCI": [".circleci/config.yml"],

        # Package Managers & Configs
        "npm": ["package.json", "package-lock.json"],
        "Yarn": ["yarn.lock", ".yarnrc.yml"],
        "pnpm": ["pnpm-lock.yaml", "pnpm-workspace.yaml"],
        "pip": ["requirements.txt", "Pipfile"],
        "Poetry": ["pyproject.toml:poetry", "poetry.lock"],
        "Maven": ["pom.xml"],
        "Gradle": ["build.gradle", "settings.gradle"],

        # Linters & Formatters
        "ESLint": [".eslintrc", "eslint.config.js"],
        "Prettier": [".prettierrc", "prettier.config.js"],
        "Black": ["pyproject.toml:black"],
        "Ruff": ["ruff.toml", "pyproject.toml:ruff"],

        # TypeScript
        "TypeScript": ["tsconfig.json", ".ts", ".tsx"],

        # Mobile
        "React Native": ["package.json:react-native"],
        "Expo": ["app.json:expo", "package.json:expo"],
        "Flutter": ["pubspec.yaml", ".dart"],
    }

    def __init__(self, client: GitHubAPIClient):
        self.client = client

    def investigate_repos(self, username: str, repositories: List[Dict], progress_callback=None) -> List[Dict]:
        """
        For each repository, fetch file tree and README content
        Detect tech stack from file patterns
        Returns enriched repository data
        """
        enriched_repos = []

        for idx, repo in enumerate(repositories, 1):
            msg = f"🔍 Investigating {repo['name']}... ({idx}/{len(repositories)})"
            print(f"  {msg}")
            if progress_callback:
                progress_callback("detective", msg)

            # Fetch repository file tree and README in one query
            repo_data = self._fetch_repo_details(username, repo["name"])

            # Detect tech stack from file patterns
            detected_tech = self._detect_tech_stack(repo_data["files"])

            # Show detected tech if any
            if detected_tech and progress_callback:
                tech_list = ', '.join(detected_tech[:3])
                if len(detected_tech) > 3:
                    tech_list += f' +{len(detected_tech)-3} more'
                tech_msg = f"  └─ {repo['name']}: {tech_list}"
                if progress_callback:
                    progress_callback("detective", tech_msg)

            # Add enriched data
            enriched = {
                **repo,
                "readme_content": repo_data["readme"],
                "detected_tech_stack": detected_tech,
                # Keep first 50 files for reference
                "file_structure": repo_data["files"][:50]
            }

            enriched_repos.append(enriched)

        return enriched_repos

    def _fetch_repo_details(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """
        Fetch repository file tree and README content in one GraphQL query
        """
        query = """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            object(expression: "HEAD:") {
              ... on Tree {
                entries {
                  name
                  type
                  path
                }
              }
            }
            readme: object(expression: "HEAD:README.md") {
              ... on Blob {
                text
              }
            }
            readmeLower: object(expression: "HEAD:readme.md") {
              ... on Blob {
                text
              }
            }
          }
        }
        """

        try:
            data = self.client.execute_query(
                query,
                {"owner": owner, "name": repo_name}
            )

            repo_data = data["repository"]
            files = []

            if repo_data["object"] and repo_data["object"]["entries"]:
                files = [
                    {"name": entry["name"], "path": entry["path"],
                        "type": entry["type"]}
                    for entry in repo_data["object"]["entries"]
                ]

            # Get README content (try both cases)
            readme_content = None
            if repo_data["readme"] and repo_data["readme"].get("text"):
                readme_content = repo_data["readme"]["text"]
            elif repo_data["readmeLower"] and repo_data["readmeLower"].get("text"):
                readme_content = repo_data["readmeLower"]["text"]

            return {
                "files": files,
                "readme": readme_content
            }
        except Exception as e:
            print(f"    ⚠️  Could not fetch details for {repo_name}: {e}")
            return {"files": [], "readme": None}

    def _detect_tech_stack(self, files: List[Dict]) -> List[str]:
        """
        Pattern match files to detect tech stack
        """
        detected = set()
        file_names = {f["name"].lower() for f in files}
        file_paths = {f["path"].lower() for f in files}
        all_files = file_names | file_paths

        for tech, patterns in self.TECH_PATTERNS.items():
            for pattern in patterns:
                pattern_lower = pattern.lower()

                # Direct file name match
                if pattern_lower in file_names:
                    detected.add(tech)
                    break

                # Path contains pattern
                elif any(pattern_lower in path for path in file_paths):
                    detected.add(tech)
                    break

                # Extension match (e.g., .tsx, .scss)
                elif pattern_lower.startswith("."):
                    if any(f.endswith(pattern_lower) for f in all_files):
                        detected.add(tech)
                        break

        return sorted(list(detected))


class LanguageAnalyzer:
    """Analyze programming languages and tech stack across repositories"""

    @staticmethod
    def analyze(repositories: List[Dict]) -> Dict[str, Any]:
        """
        Analyze language distribution, tech stack, and expertise
        No API calls - works with already fetched data
        """
        # Collect all languages with their sizes
        language_stats = Counter()
        language_colors = {}
        all_topics = []

        for repo in repositories:
            if not repo.get("is_fork") and not repo.get("is_archived"):
                for lang in repo.get("languages", []):
                    language_stats[lang["name"]] += lang["size"]
                    language_colors[lang["name"]] = lang["color"]

                all_topics.extend(repo.get("topics", []))

        # Calculate percentages
        total_size = sum(language_stats.values())
        language_percentages = {
            lang: {
                "size": size,
                "percentage": round((size / total_size * 100), 2) if total_size > 0 else 0,
                "color": language_colors.get(lang)
            }
            for lang, size in language_stats.most_common()
        }

        # Analyze topics for tech stack
        topic_frequency = Counter(all_topics)

        return {
            "languages": language_percentages,
            "top_languages": list(language_stats.most_common(10)),
            "tech_stack": topic_frequency.most_common(20),
            "total_languages": len(language_stats)
        }


class ContributionCalendar:
    """Analyze contribution patterns, streaks, and activity"""

    @staticmethod
    def analyze(contribution_data: Dict) -> Dict[str, Any]:
        """
        Analyze contribution patterns from already fetched data
        No additional API calls needed
        """
        calendar = contribution_data["calendar"]

        # Flatten all contribution days
        all_days = []
        for week in calendar:
            all_days.extend(week["contributionDays"])

        # Calculate current streak
        current_streak = 0
        for day in reversed(all_days):
            if day["contributionCount"] > 0:
                current_streak += 1
            else:
                break

        # Calculate longest streak
        longest_streak = 0
        temp_streak = 0
        for day in all_days:
            if day["contributionCount"] > 0:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 0

        # Find most productive day
        most_productive_day = max(
            all_days, key=lambda x: x["contributionCount"])

        # Calculate average contributions
        total_days = len(all_days)
        active_days = sum(
            1 for day in all_days if day["contributionCount"] > 0)
        total_contributions = sum(day["contributionCount"] for day in all_days)

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_contributions": contribution_data["total"],
            "average_daily": round(total_contributions / total_days, 2) if total_days > 0 else 0,
            "active_days": active_days,
            "most_productive_day": {
                "date": most_productive_day["date"],
                "contributions": most_productive_day["contributionCount"]
            },
            "activity_rate": round((active_days / total_days * 100), 2) if total_days > 0 else 0
        }


class SkillExtractor:
    """Extract skills and technologies from repositories"""

    @staticmethod
    def extract(repositories: List[Dict]) -> Dict[str, Any]:
        """
        Extract skills from repo topics, descriptions, and languages
        No API calls - works with cached data
        """
        skills = set()
        frameworks = set()
        tools = set()

        # Common framework and tool keywords
        framework_keywords = {
            'react', 'vue', 'angular', 'django', 'flask', 'express', 'fastapi',
            'spring', 'laravel', 'rails', 'nextjs', 'nuxt', 'svelte', 'nest'
        }

        tool_keywords = {
            'docker', 'kubernetes', 'jenkins', 'github-actions', 'terraform',
            'ansible', 'webpack', 'vite', 'babel', 'eslint', 'pytest', 'jest'
        }

        for repo in repositories:
            # Extract from topics
            for topic in repo.get("topics", []):
                topic_lower = topic.lower()
                if topic_lower in framework_keywords:
                    frameworks.add(topic)
                elif topic_lower in tool_keywords:
                    tools.add(topic)
                else:
                    skills.add(topic)

            # Extract from languages
            for lang in repo.get("languages", []):
                skills.add(lang["name"])

        return {
            "all_skills": sorted(list(skills)),
            "frameworks": sorted(list(frameworks)),
            "tools": sorted(list(tools)),
            "total_unique_skills": len(skills) + len(frameworks) + len(tools)
        }


class SocialProofCollector:
    """Aggregate social proof metrics across all repositories"""

    @staticmethod
    def collect(repositories: List[Dict], profile: Dict) -> Dict[str, Any]:
        """
        Calculate total stars, forks, and other social proof metrics
        No API calls - aggregates existing data
        """
        total_stars = sum(repo.get("stars", 0) for repo in repositories)
        total_forks = sum(repo.get("forks", 0) for repo in repositories)

        # Find most starred repo
        most_starred = max(repositories, key=lambda x: x.get(
            "stars", 0)) if repositories else None

        # Count repos by activity
        active_repos = sum(
            1 for repo in repositories if not repo.get("is_archived"))
        original_repos = sum(
            1 for repo in repositories if not repo.get("is_fork"))

        return {
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_followers": profile["stats"]["followers"],
            "total_repos": profile["stats"]["total_repos"],
            "active_repos": active_repos,
            "original_repos": original_repos,
            "most_starred_repo": {
                "name": most_starred["name"],
                "stars": most_starred["stars"],
                "url": most_starred["url"]
            } if most_starred else None,
            "average_stars_per_repo": round(total_stars / len(repositories), 2) if repositories else 0
        }


# Main orchestrator
class GitHubProfileAnalyzer:
    """Main class that orchestrates all tools"""

    def __init__(self, github_token: str):
        self.client = GitHubAPIClient(github_token)
        self.profile_detective = ProfileDetective(self.client)
        self.repo_stalker = RepositoryStalker(self.client)
        self.ex_readme = ExReadme(self.client)
        self.tech_detective = TechStackDetective(self.client)

    def analyze_user(self, username: str) -> Dict[str, Any]:
        """
        Complete user analysis with ALL tools
        Only 2 API calls total:
        1. ProfileDetective (gets everything)
        2. ExReadme (gets existing README)
        """
        print(f"🔍 Investigating {username}'s profile...")

        # API Call #1: Get complete profile
        profile = self.profile_detective.investigate(username)

        print(f"✅ Profile data fetched!")
        print(f"📊 Found {len(profile['repositories'])} repositories")

        # API Call #2: Get existing README (if exists)
        existing_readme = self.ex_readme.read(username)

        print(
            f"📄 Existing README: {'Found' if existing_readme else 'Not found'}")

        # Now run all analysis tools
        print("🔬 Analyzing repositories...")
        enhanced_repos = self.repo_stalker.stalk(
            username,
            profile["repositories"],
            profile["pinned_repos"]
        )

        print(f"✅ Selected {len(enhanced_repos)} unique repositories")

        # Deep dive into each repo - fetch file structure, README, detect tech stack
        print(
            "🔍 Deep diving into repositories (fetching READMEs & detecting tech stacks)...")
        enriched_repos = self.tech_detective.investigate_repos(
            username,
            enhanced_repos
        )

        print("💻 Analyzing languages...")
        language_analysis = LanguageAnalyzer.analyze(enriched_repos)

        print("📈 Analyzing contributions...")
        contribution_analysis = ContributionCalendar.analyze(
            profile["contributions"])

        print("🎯 Extracting skills...")
        skills = SkillExtractor.extract(enriched_repos)

        print("⭐ Collecting social proof...")
        social_proof = SocialProofCollector.collect(enriched_repos, profile)

        # Compile everything
        complete_analysis = {
            "profile": profile["basic_info"],
            "stats": profile["stats"],
            "contributions": contribution_analysis,
            "repositories": enriched_repos,
            "pinned_repos": profile["pinned_repos"],
            "languages": language_analysis,
            "skills": skills,
            "social_proof": social_proof,
            "social_accounts": profile["social_accounts"],
            "existing_readme": existing_readme
        }

        print("✨ Analysis complete!")
        return complete_analysis


def main():
    """Comprehensive test of all GitHub Profile Analyzer tools"""
    print("=" * 70)
    print("🚀 GRWM - GitHub README With Me")
    print("   Testing All Tools & Components")
    print("=" * 70)

    if not GITHUB_TOKEN:
        print("\n❌ Error: GITHUB_PAT not found in environment variables")
        print("Please add your GitHub Personal Access Token to .env file")
        print("\nSteps to fix:")
        print("1. Copy .env.example to .env")
        print("2. Add your GitHub PAT to the GITHUB_PAT variable")
        print("3. Get your PAT from: https://github.com/settings/tokens")
        return

    # Test with a username
    username = input("\n👤 Enter GitHub username to analyze: ").strip()
    if not username:
        print("❌ Username cannot be empty")
        return

    print(f"\n{'='*70}")
    print(f"🔬 Starting Comprehensive Analysis for @{username}")
    print(f"{'='*70}\n")

    # Initialize analyzer
    analyzer = GitHubProfileAnalyzer(GITHUB_TOKEN)

    try:
        # Run the full analysis
        result = analyzer.analyze_user(username)

        # ============================================================
        # Display Comprehensive Results
        # ============================================================

        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE ANALYSIS RESULTS")
        print("=" * 70)

        # ============================================================
        # 1. PROFILE DETECTIVE RESULTS
        # ============================================================
        print("\n" + "─" * 70)
        print("🔍 1. PROFILE DETECTIVE - Basic Profile Information")
        print("─" * 70)
        profile = result['profile']
        print(f"Name:            {profile['name']}")
        print(f"Username:        @{username}")
        print(f"Bio:             {profile['bio'][:100]}..." if profile['bio'] and len(
            profile['bio']) > 100 else f"Bio:             {profile['bio']}")
        print(f"Company:         {profile['company'] or 'N/A'}")
        print(f"Location:        {profile['location'] or 'N/A'}")
        print(f"Email:           {profile['email'] or 'N/A'}")
        print(f"Website:         {profile['website'] or 'N/A'}")
        print(
            f"Twitter:         @{profile['twitter']}" if profile['twitter'] else "Twitter:         N/A")
        print(
            f"Hireable:        {'Yes ✓' if profile['is_hireable'] else 'No'}")
        print(f"Member Since:    {profile['created_at'][:10]}")

        if profile['status']:
            print(
                f"Status:          {profile['status']['emoji']} {profile['status']['message']}")

        # Social accounts
        if result['social_accounts']:
            print(f"\n🔗 Social Accounts:")
            for acc in result['social_accounts']:
                print(f"  - {acc['provider']}: {acc['url']}")

        # ============================================================
        # 2. REPOSITORY STALKER RESULTS
        # ============================================================
        print("\n" + "─" * 70)
        print(
            f"📦 2. REPOSITORY STALKER - Selected {len(result['repositories'])} Repositories")
        print("─" * 70)
        print(f"Total Repositories:     {result['stats']['total_repos']}")
        print(
            f"Analyzed Repositories:  {len(result['repositories'])} (Guaranteed Unique)")
        print(
            f"Pinned Repositories:    {sum(1 for r in result['repositories'] if r.get('is_pinned'))}")
        print(f"\nTop Repositories:")
        for i, repo in enumerate(result['repositories'][:5], 1):
            pinned = "📌 " if repo.get('is_pinned') else "   "
            print(
                f"  {pinned}{i}. {repo['name']} - ⭐ {repo['stars']} | 🍴 {repo['forks']}")
            print(f"      {repo['description'][:70]}..." if repo['description'] and len(
                repo['description']) > 70 else f"      {repo['description']}")

        if len(result['repositories']) > 5:
            print(
                f"  ... and {len(result['repositories']) - 5} more repositories")

        # ============================================================
        # 3. EXREADME RESULTS
        # ============================================================
        print("\n" + "─" * 70)
        print("📄 3. EXREADME - Existing Profile README")
        print("─" * 70)
        if result['existing_readme']:
            readme_preview = result['existing_readme'][:200].replace('\n', ' ')
            print(f"Status:    Found ✓")
            print(f"Length:    {len(result['existing_readme'])} characters")
            print(f"Preview:   {readme_preview}...")
        else:
            print(
                "Status:    Not found (No {username}/{username} repository or README.md)")

        # ============================================================
        # 4. TECHSTACK DETECTIVE RESULTS
        # ============================================================
        print("\n" + "─" * 70)
        print("🔧 4. TECHSTACK DETECTIVE - Detected Technologies")
        print("─" * 70)
        all_tech = set()
        repo_tech_count = {}
        repos_with_readme = 0

        for repo in result['repositories']:
            tech_stack = repo.get('detected_tech_stack', [])
            all_tech.update(tech_stack)
            if tech_stack:
                repo_tech_count[repo['name']] = len(tech_stack)
            if repo.get('readme_content'):
                repos_with_readme += 1

        print(f"Total Technologies Detected:    {len(all_tech)}")
        print(
            f"Repositories with READMEs:      {repos_with_readme} / {len(result['repositories'])}")
        print(f"\n🏆 All Detected Technologies:")
        if all_tech:
            # Group technologies for better display
            tech_list = sorted(list(all_tech))
            for i in range(0, len(tech_list), 5):
                print(f"  {', '.join(tech_list[i:i+5])}")
        else:
            print("  None detected")

        print(f"\n📊 Top 5 Repos by Tech Stack Diversity:")
        sorted_repos = sorted(repo_tech_count.items(),
                              key=lambda x: x[1], reverse=True)[:5]
        for repo_name, tech_count in sorted_repos:
            repo_data = next(
                r for r in result['repositories'] if r['name'] == repo_name)
            print(f"  • {repo_name}: {tech_count} technologies")
            print(
                f"    → {', '.join(repo_data.get('detected_tech_stack', [])[:8])}")

        # ============================================================
        # 5. LANGUAGE ANALYZER RESULTS
        # ============================================================
        print("\n" + "─" * 70)
        print("💻 5. LANGUAGE ANALYZER - Programming Languages")
        print("─" * 70)
        print(
            f"Total Languages:        {result['languages']['total_languages']}")
        print(f"\nTop Languages by Usage:")
        for i, (lang, count) in enumerate(result['languages']['top_languages'][:8], 1):
            lang_info = result['languages']['languages'].get(lang, {})
            percentage = lang_info.get('percentage', 0)
            print(f"  {i}. {lang:20} - {count:>10,} bytes ({percentage:>5.1f}%)")

        print(f"\nTech Stack from Topics:")
        for i, (topic, count) in enumerate(result['languages']['tech_stack'][:10], 1):
            print(f"  {i}. {topic:20} - used in {count} repositories")

        # ============================================================
        # 6. CONTRIBUTION CALENDAR RESULTS
        # ============================================================
        print("\n" + "─" * 70)
        print("📈 6. CONTRIBUTION CALENDAR - Activity Analysis")
        print("─" * 70)
        contrib = result['contributions']
        print(
            f"Total Contributions:        {contrib['total_contributions']:,}")
        print(
            f"Current Streak:             {contrib['current_streak']} days 🔥")
        print(
            f"Longest Streak:             {contrib['longest_streak']} days 🏆")
        print(
            f"Average Daily:              {contrib['average_daily']} contributions")
        print(f"Active Days:                {contrib['active_days']:,} days")
        print(f"Activity Rate:              {contrib['activity_rate']}%")
        print(
            f"Most Productive Day:        {contrib['most_productive_day']['date']} ({contrib['most_productive_day']['contributions']} contributions)")

        # ============================================================
        # 7. SKILL EXTRACTOR RESULTS
        # ============================================================
        print("\n" + "─" * 70)
        print("🎯 7. SKILL EXTRACTOR - Skills & Technologies")
        print("─" * 70)
        skills = result['skills']
        print(f"Total Unique Skills:    {skills['total_unique_skills']}")
        print(f"\nFrameworks ({len(skills['frameworks'])}):")
        print(
            f"  {', '.join(skills['frameworks'][:15]) if skills['frameworks'] else 'None detected'}")
        print(f"\nTools ({len(skills['tools'])}):")
        print(
            f"  {', '.join(skills['tools'][:15]) if skills['tools'] else 'None detected'}")
        print(f"\nOther Skills ({len(skills['all_skills'])}):")
        print(
            f"  {', '.join(skills['all_skills'][:20]) if skills['all_skills'] else 'None detected'}")

        # ============================================================
        # 8. SOCIAL PROOF COLLECTOR RESULTS
        # ============================================================
        print("\n" + "─" * 70)
        print("⭐ 8. SOCIAL PROOF COLLECTOR - GitHub Metrics")
        print("─" * 70)
        social = result['social_proof']
        print(f"Total Stars:                {social['total_stars']:,} ⭐")
        print(f"Total Forks:                {social['total_forks']:,} 🍴")
        print(f"Total Followers:            {social['total_followers']:,} 👥")
        print(f"Total Repositories:         {social['total_repos']:,} 📦")
        print(f"Active Repositories:        {social['active_repos']:,}")
        print(f"Original Repositories:      {social['original_repos']:,}")
        print(
            f"Average Stars per Repo:     {social['average_stars_per_repo']:.2f}")

        if social['most_starred_repo']:
            print(f"\n🏆 Most Starred Repository:")
            print(f"  Name:   {social['most_starred_repo']['name']}")
            print(f"  Stars:  {social['most_starred_repo']['stars']:,} ⭐")
            print(f"  URL:    {social['most_starred_repo']['url']}")

        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 70)
        print("✨ ANALYSIS COMPLETE - ALL TOOLS TESTED SUCCESSFULLY")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"  ✓ ProfileDetective      - Fetched complete profile")
        print(
            f"  ✓ RepositoryStalker     - Analyzed {len(result['repositories'])} unique repositories")
        print(
            f"  ✓ ExReadme              - {'Found' if result['existing_readme'] else 'Not found'}")
        print(
            f"  ✓ TechStackDetective    - Detected {len(all_tech)} technologies")
        print(
            f"  ✓ LanguageAnalyzer      - Analyzed {result['languages']['total_languages']} languages")
        print(
            f"  ✓ ContributionCalendar  - Processed {contrib['total_contributions']:,} contributions")
        print(
            f"  ✓ SkillExtractor        - Extracted {skills['total_unique_skills']} skills")
        print(
            f"  ✓ SocialProofCollector  - Collected {social['total_stars']:,} total stars")

        print(f"\n🎯 Ready for AI Agent Integration!")
        print("=" * 70)

        return result

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
