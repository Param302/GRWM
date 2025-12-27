"""
Test Script for GRWM Agents
Run this to test each agent independently as they're built
"""

from agents import (
    create_detective_graph,
    create_initial_state,
    DetectiveAgent,
    CTOAgent,
    GhostwriterAgent,
    GITHUB_TOKEN,
    GOOGLE_API_KEY,
)
import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import our agents


def print_section(title: str):
    """Pretty print section headers"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title: str):
    """Pretty print subsection headers"""
    print("\n" + "─" * 70)
    print(f"  {title}")
    print("─" * 70)


def check_environment():
    """Check if all required environment variables are set"""
    print_section("🔧 Environment Check")

    issues = []

    if not GITHUB_TOKEN:
        issues.append("❌ GITHUB_PAT not found")
        print("❌ GITHUB_PAT: Not Set")
        print("   → Get one at: https://github.com/settings/tokens")
    else:
        print(f"✅ GITHUB_PAT: Set (length: {len(GITHUB_TOKEN)})")

    if not GOOGLE_API_KEY:
        issues.append("❌ GOOGLE_API_KEY not found")
        print("❌ GOOGLE_API_KEY: Not Set")
        print("   → Get one at: https://makersuite.google.com/app/apikey")
    else:
        print(f"✅ GOOGLE_API_KEY: Set (length: {len(GOOGLE_API_KEY)})")

    if issues:
        print("\n⚠️  Please fix the above issues before continuing")
        print("   1. Copy .env.example to .env")
        print("   2. Add your API keys")
        return False

    print("\n✅ All environment variables are set!")
    return True


def test_detective_standalone():
    """Test Detective agent without the graph"""
    print_section("🔍 Testing Detective Agent (Standalone)")

    username = input("\n👤 Enter GitHub username to test: ").strip()
    if not username:
        print("❌ Username required")
        return None

    try:
        print(f"\n🚀 Initializing Detective...")
        detective = DetectiveAgent(GITHUB_TOKEN)

        print(f"🔍 Starting investigation...")
        raw_data = asyncio.run(detective.investigate_parallel(username))

        print_subsection("📊 Results Summary")
        print(f"Profile Name:       {raw_data['profile']['name']}")
        print(f"Username:           @{username}")
        print(f"Bio:                {raw_data['profile']['bio'][:80]}..." if raw_data['profile']['bio'] and len(
            raw_data['profile']['bio']) > 80 else f"Bio:                {raw_data['profile']['bio']}")
        print(
            f"Location:           {raw_data['profile']['location'] or 'N/A'}")
        print(f"Followers:          {raw_data['stats']['followers']:,}")
        print(f"Total Repos:        {raw_data['stats']['total_repos']:,}")
        print(
            f"Total Stars:        {raw_data['social_proof']['total_stars']:,}")
        print(
            f"Total Forks:        {raw_data['social_proof']['total_forks']:,}")
        print(
            f"Repositories:       {len(raw_data['repositories'])} (analyzed)")
        print(
            f"Has Profile README: {'Yes ✓' if raw_data['existing_readme'] else 'No'}")

        print_subsection("📦 Top 5 Repositories")
        for i, repo in enumerate(raw_data['repositories'][:5], 1):
            pinned = "📌" if repo.get('is_pinned') else "  "
            print(f"{pinned} {i}. {repo['name']}")
            print(
                f"      ⭐ {repo['stars']} | 🍴 {repo['forks']} | {repo['primary_language'] or 'N/A'}")
            print(
                f"      Tech: {', '.join(repo.get('detected_tech_stack', [])[:5]) or 'None detected'}")
            print(
                f"      README: {'✓' if repo.get('readme_content') else '✗'}")

        print_subsection("🔧 Technology Overview")
        all_tech = set()
        repos_with_readme = 0
        for repo in raw_data['repositories']:
            all_tech.update(repo.get('detected_tech_stack', []))
            if repo.get('readme_content'):
                repos_with_readme += 1

        print(f"Detected Technologies: {len(all_tech)}")
        if all_tech:
            tech_list = sorted(list(all_tech))
            for i in range(0, len(tech_list), 6):
                print(f"  {', '.join(tech_list[i:i+6])}")

        print(
            f"\nREADME Coverage: {repos_with_readme}/{len(raw_data['repositories'])} repositories")

        print("\n✅ Detective standalone test passed!")
        return raw_data

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_cto_standalone(raw_data: dict = None):
    """Test CTO agent without the graph (requires Detective data)"""
    print_section("🧠 Testing CTO Agent (Standalone)")

    # Get data from Detective if not provided
    if not raw_data:
        print("⚠️  No raw data provided. Running Detective first...")
        raw_data = test_detective_standalone()
        if not raw_data:
            print("❌ Cannot test CTO without Detective data")
            return None

    try:
        print(f"\n🚀 Initializing CTO...")
        cto = CTOAgent()

        print(f"🧠 Starting analysis...")
        analysis = cto.analyze(raw_data)

        print_subsection("📊 Analysis Summary")

        # Developer Archetype
        print(f"Developer Archetype:")
        print(f"  Primary:    {analysis['developer_archetype']['primary']}")
        print(f"  Secondary:  {analysis['developer_archetype']['secondary']}")
        print(f"  Full Title: {analysis['developer_archetype']['full_title']}")

        # Personality Comment
        print(f"\n💬 CTO's Verdict:")
        print(f"  \"{analysis['skill_domains']['personality_comment']}\"")

        # Grind Score
        print(f"\nGrind Score:")
        print(
            f"  Score:  {analysis['grind_score']['score']} {analysis['grind_score']['emoji']}")
        print(f"  Label:  {analysis['grind_score']['label']}")
        print(f"  Breakdown:")
        for key, value in analysis['grind_score']['breakdown'].items():
            print(f"    - {key}: {value}")

        # Language Dominance
        print(f"\nLanguage Dominance:")
        primary_lang = analysis['language_dominance']['primary_language']
        print(
            f"  Primary: {primary_lang['name']} ({primary_lang['percentage']}%)")
        print(
            f"  Specialist: {'Yes ✓' if analysis['language_dominance']['is_specialist'] else 'No'}")
        print(f"  Top 5 Languages:")
        for lang in analysis['language_dominance']['top_5_languages']:
            print(f"    - {lang['name']}: {lang['percentage']}%")

        # Skill Domains
        print(f"\nSkill Domains:")
        print(f"  Domain Count: {analysis['skill_domains']['domain_count']}")
        print(
            f"  Full Stack: {'Yes ✓' if analysis['skill_domains']['is_full_stack'] else 'No'}")
        print(f"  Primary Domains:")
        for domain in analysis['skill_domains']['primary_domains']:
            print(f"    - {domain['name']} (score: {domain['score']})")
            print(
                f"      Technologies: {', '.join(domain['technologies'][:5])}")

        # Tech Diversity
        print(f"\nTech Diversity:")
        print(
            f"  Classification: {analysis['tech_diversity']['classification']}")
        print(f"  Description: {analysis['tech_diversity']['description']}")
        print(
            f"  Total Technologies: {analysis['tech_diversity']['total_technologies']}")
        print(
            f"  Diversity Score: {analysis['tech_diversity']['diversity_score']}")
        print(f"  Category Breakdown:")
        for category, count in analysis['tech_diversity']['category_breakdown'].items():
            print(f"    - {category}: {count}")

        # Key Projects
        print(f"\nKey Projects:")
        for i, project in enumerate(analysis['key_projects'], 1):
            print(
                f"  {i}. {project['name']} (Complexity: {project['complexity_score']})")
            print(
                f"     ⭐ {project['stars']} | 🍴 {project['forks']} | {project['primary_language'] or 'N/A'}")
            print(f"     Tech: {', '.join(project['tech_stack'][:5])}")

        # Impact Metrics
        print(f"\nImpact Metrics:")
        print(f"  Impact Score: {analysis['impact_metrics']['impact_score']}")
        print(f"  Total Stars: {analysis['impact_metrics']['total_stars']:,}")
        print(f"  Total Forks: {analysis['impact_metrics']['total_forks']:,}")
        print(
            f"  Engagement Rate: {analysis['impact_metrics']['engagement_rate']}%")
        print(
            f"  Contribution Intensity: {analysis['impact_metrics']['contribution_intensity']}/day")

        # Summary
        print_subsection("📝 Summary")
        print(analysis['summary'])

        print("\n✅ CTO standalone test passed!")
        return analysis

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_detective_with_graph():
    """Test Detective agent within the LangGraph"""
    print_section("🤖 Testing Detective Agent (LangGraph Integration)")

    username = input("\n👤 Enter GitHub username to test: ").strip()
    if not username:
        print("❌ Username required")
        return None

    try:
        print(f"\n🚀 Creating LangGraph...")
        app = create_detective_graph()

        print(f"📊 Creating initial state...")
        initial_state = create_initial_state(username)

        print(f"🤖 Running graph with streaming...")
        print("─" * 70)

        # Config with thread_id (required for checkpointer)
        config = {
            "configurable": {"thread_id": f"test_{username}"},
            "recursion_limit": 10
        }

        final_state = None
        for event in app.stream(initial_state, config):
            # Print event type
            event_name = list(event.keys())[0]
            print(f"\n📡 Event: {event_name}")

            # Extract state from event
            if "detective" in event:
                state = event["detective"]

                # Check for errors
                if state.get("error"):
                    print(f"   ❌ Error: {state['error']}")
                    print(f"   🔄 Retry count: {state.get('retry_count', 0)}")

                # Check for success
                elif state.get("raw_data"):
                    print(f"   ✅ Detective completed!")
                    print(
                        f"   📦 Repositories: {len(state['raw_data']['repositories'])}")
                    print(
                        f"   ⭐ Total Stars: {state['raw_data']['social_proof']['total_stars']:,}")
                    final_state = state

            # Check CTO
            if "cto" in event:
                state = event["cto"]

                # Check for errors
                if state.get("error"):
                    print(f"   ❌ Error: {state['error']}")

                # Check for success
                elif state.get("analysis"):
                    analysis = state['analysis']
                    print(f"   ✅ CTO completed!")
                    print(
                        f"   🎯 Archetype: {analysis['developer_archetype']['full_title']}")
                    print(
                        f"   {analysis['grind_score']['emoji']} Grind: {analysis['grind_score']['score']} ({analysis['grind_score']['label']})")
                    print(
                        f"   💻 Primary: {analysis['language_dominance']['primary_language']['name']} ({analysis['language_dominance']['primary_language']['percentage']}%)")
                    final_state = state
                    final_state = state

        print("\n" + "─" * 70)

        if final_state and final_state.get("raw_data"):
            print_subsection("📊 Final State Summary")
            print(f"Username:        @{final_state['username']}")
            print(f"Error:           {final_state.get('error') or 'None'}")
            print(f"Retry Count:     {final_state.get('retry_count', 0)}")
            print(f"Messages:        {len(final_state.get('messages', []))}")
            print(f"Data Collected:  ✓")

            # Show intermediate results
            if final_state.get("intermediate_results"):
                print(f"\nIntermediate Results:")
                for key, value in final_state["intermediate_results"].items():
                    print(f"  - {key}: {value}")

            print("\n✅ Graph execution test passed!")
            return final_state
        else:
            print("\n⚠️  Graph executed but no data collected")
            return None

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_test_results(data: dict, username: str):
    """Save test results to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{username}_{timestamp}.json"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"✅ Saved to: {filename}")
    except Exception as e:
        print(f"❌ Failed to save: {e}")


def test_ghostwriter_standalone(raw_data: dict, analysis: dict):
    """Test Ghostwriter agent without the graph"""
    print_section("✍️  Testing Ghostwriter Agent (Standalone)")

    if not raw_data or not analysis:
        print("❌ Need Detective data and CTO analysis first")
        return None

    try:
        print(f"\n🚀 Initializing Ghostwriter...")
        ghostwriter = GhostwriterAgent()

        # Get tone preference
        print("\n🎨 README Tone Options:")
        print("1. Professional (polished, business-ready)")
        print("2. GenZ (casual, relatable vibes)")
        print("3. Minimalist (clean, data-focused)")
        print("4. Creative (unique, storytelling)")

        tone_choice = input("Select tone (1-4, default=1): ").strip()
        tone_map = {"1": "professional", "2": "genz",
                    "3": "minimalist", "4": "creative"}
        tone = tone_map.get(tone_choice, "professional")

        # Create mock state
        from agents import AgentState
        state = {
            "username": raw_data['profile']['login'],
            "user_preferences": {"tone": tone, "style": "modern"},
            "raw_data": raw_data,
            "analysis": analysis,
            "final_markdown": None,
            "messages": [],
            "error": None,
            "retry_count": 0,
            "intermediate_results": {},
            "revision_instructions": None,
            "generation_history": [],
        }

        print(f"✍️  Generating README with {tone} tone...")
        result = ghostwriter(state)

        if result.get("final_markdown"):
            markdown = result["final_markdown"]

            print_subsection("📊 Results Summary")
            print(f"Markdown Length:    {len(markdown):,} characters")
            print(f"Lines:              {len(markdown.split(chr(10))):,}")
            print(
                f"Version:            {len(result.get('generation_history', []))}")
            print(f"Tone:               {tone.title()}")

            # Preview first 500 chars
            print("\n" + "─" * 70)
            print("📝 Preview (first 500 chars):")
            print("─" * 70)
            print(markdown[:500])
            if len(markdown) > 500:
                print("...")

            # Ask to see full
            show_full = input(
                "\n📄 Show full README? (y/n): ").strip().lower()
            if show_full == 'y':
                print("\n" + "=" * 70)
                print("📝 FULL README.md")
                print("=" * 70 + "\n")
                print(markdown)
                print("\n" + "=" * 70)

            # Ask to save
            save = input("\n💾 Save to file? (y/n): ").strip().lower()
            if save == 'y':
                filename = f"README_{state['username']}.md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(markdown)
                print(f"✅ Saved to {filename}")

            print("\n✅ Ghostwriter test passed!")
            return result

        else:
            print("\n⚠️  No markdown generated")
            return None

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_complete_pipeline():
    """Test the complete agent pipeline: Detective → CTO → Ghostwriter"""
    print_section(
        "🚀 Testing Complete Pipeline (Detective → CTO → Ghostwriter)")

    username = input("\n👤 Enter GitHub username to test: ").strip()
    if not username:
        print("❌ Username required")
        return None

    # Get tone preference
    print("\n🎨 README Tone Options:")
    print("1. Professional (polished, business-ready)")
    print("2. GenZ (casual, relatable vibes)")
    print("3. Minimalist (clean, data-focused)")
    print("4. Creative (unique, storytelling)")

    tone_choice = input("Select tone (1-4, default=1): ").strip()
    tone_map = {"1": "professional", "2": "genz",
                "3": "minimalist", "4": "creative"}
    tone = tone_map.get(tone_choice, "professional")

    try:
        print(f"\n🚀 Creating Complete LangGraph...")
        app = create_detective_graph()

        print(f"📊 Creating initial state...")
        initial_state = create_initial_state(
            username,
            preferences={"tone": tone, "style": "modern"}
        )

        print(f"🤖 Running complete pipeline with streaming...")
        print("─" * 70)

        # Config with thread_id (required for checkpointer)
        config = {
            "configurable": {"thread_id": f"complete_{username}"},
            "recursion_limit": 15
        }

        final_state = None
        for event in app.stream(initial_state, config):
            # Print event type
            event_name = list(event.keys())[0]
            print(f"\n📡 Event: {event_name}")

            # Extract state from event
            if "detective" in event:
                state = event["detective"]
                if state.get("error"):
                    print(f"   ❌ Error: {state['error']}")
                elif state.get("raw_data"):
                    print(f"   ✅ Detective completed!")
                    print(
                        f"   📦 Repositories: {len(state['raw_data']['repositories'])}")
                    final_state = state

            if "cto" in event:
                state = event["cto"]
                if state.get("error"):
                    print(f"   ❌ Error: {state['error']}")
                elif state.get("analysis"):
                    print(f"   ✅ CTO completed!")
                    print(
                        f"   🎯 Archetype: {state['analysis']['developer_archetype']['full_title']}")
                    final_state = state

            if "ghostwriter" in event:
                state = event["ghostwriter"]
                if state.get("error"):
                    print(f"   ❌ Error: {state['error']}")
                elif state.get("final_markdown"):
                    markdown = state["final_markdown"]
                    print(f"   ✅ Ghostwriter completed!")
                    print(f"   📝 Length: {len(markdown):,} characters")
                    print(f"   📄 Lines: {len(markdown.split(chr(10))):,}")
                    final_state = state

        print("\n" + "─" * 70)

        if final_state and final_state.get("final_markdown"):
            print_subsection("📊 Pipeline Results")
            print(f"Username:           @{final_state['username']}")
            print(
                f"Repositories:       {len(final_state['raw_data']['repositories'])}")
            print(
                f"Total Stars:        {final_state['raw_data']['social_proof']['total_stars']:,}")
            print(
                f"Archetype:          {final_state['analysis']['developer_archetype']['full_title']}")
            print(
                f"Grind Score:        {final_state['analysis']['grind_score']['score']} ({final_state['analysis']['grind_score']['label']})")
            print(
                f"README Length:      {len(final_state['final_markdown']):,} chars")
            print(f"Tone:               {tone.title()}")

            # Show preview
            markdown = final_state["final_markdown"]
            print("\n" + "─" * 70)
            print("📝 Preview (first 500 chars):")
            print("─" * 70)
            print(markdown[:500])
            if len(markdown) > 500:
                print("...")

            # Ask to see full
            show_full = input(
                "\n📄 Show full README? (y/n): ").strip().lower()
            if show_full == 'y':
                print("\n" + "=" * 70)
                print("📝 FULL README.md")
                print("=" * 70 + "\n")
                print(markdown)
                print("\n" + "=" * 70)

            # Ask to save
            save = input("\n💾 Save to file? (y/n): ").strip().lower()
            if save == 'y':
                filename = f"README_{username}.md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(markdown)
                print(f"✅ Saved to {filename}")

            print("\n✅ Complete pipeline test passed!")
            return final_state
        else:
            print("\n⚠️  Pipeline executed but README not generated")
            return None

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_test_results_old(data: dict, username: str):
    """Save test results to JSON for inspection"""
    if not data:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{username}_{timestamp}.json"

    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"\n💾 Test results saved to: {filename}")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")


def main():
    """Main test menu"""
    print("=" * 70)
    print("🧪 GRWM - Agent Testing Suite")
    print("=" * 70)

    # Check environment
    if not check_environment():
        return

    # Test menu
    while True:
        print_section("🧪 Test Menu")
        print("1. Test Detective (Standalone)")
        print("2. Test CTO (Standalone - requires Detective data)")
        print("3. Test Ghostwriter (Standalone - requires Detective + CTO)")
        print("4. Test Detective + CTO (LangGraph Integration)")
        print("5. Test Complete Pipeline (Detective + CTO + Ghostwriter)")
        print("6. Run All Tests")
        print("7. Exit")

        choice = input("\n👉 Select option (1-7): ").strip()

        if choice == "1":
            result = test_detective_standalone()
            if result:
                save = input(
                    "\n💾 Save results to JSON? (y/n): ").strip().lower()
                if save == "y":
                    save_test_results(result, result['profile']['login'])

        elif choice == "2":
            # Need Detective data first
            print("\n⚠️  CTO requires Detective data. Running Detective first...")
            detective_data = test_detective_standalone()
            if detective_data:
                result = test_cto_standalone(detective_data)
                if result:
                    save = input(
                        "\n💾 Save analysis to JSON? (y/n): ").strip().lower()
                    if save == "y":
                        save_test_results(
                            result, detective_data['profile']['login'])

        elif choice == "3":
            # Need Detective + CTO data first
            print(
                "\n⚠️  Ghostwriter requires Detective + CTO data. Running both first...")
            detective_data = test_detective_standalone()
            if detective_data:
                cto_data = test_cto_standalone(detective_data)
                if cto_data:
                    result = test_ghostwriter_standalone(
                        detective_data, cto_data)

        elif choice == "4":
            result = test_detective_with_graph()
            if result and (result.get("raw_data") or result.get("analysis")):
                save = input(
                    "\n💾 Save results to JSON? (y/n): ").strip().lower()
                if save == "y":
                    save_test_results(result, result['username'])

        elif choice == "5":
            result = test_complete_pipeline()
            if result:
                save = input(
                    "\n💾 Save complete results to JSON? (y/n): ").strip().lower()
                if save == "y":
                    save_test_results(result, result['username'])

        elif choice == "6":
            username = input("\n👤 Enter GitHub username: ").strip()
            if username:
                # Detective standalone
                print("\n" + "=" * 70)
                print("TEST 1: Detective Standalone")
                print("=" * 70)
                result1 = test_detective_standalone()

                # CTO standalone (if Detective succeeded)
                result2 = None
                if result1:
                    print("\n" + "=" * 70)
                    print("TEST 2: CTO Standalone")
                    print("=" * 70)
                    result2 = test_cto_standalone(result1)

                # Ghostwriter standalone (if CTO succeeded)
                result3 = None
                if result2:
                    print("\n" + "=" * 70)
                    print("TEST 3: Ghostwriter Standalone")
                    print("=" * 70)
                    result3 = test_ghostwriter_standalone(result1, result2)

                # Complete pipeline test
                print("\n" + "=" * 70)
                print("TEST 4: Complete Pipeline (LangGraph)")
                print("=" * 70)
                result4 = test_complete_pipeline()

                # Save if all successful
                if result1 and result2 and result3 and result4:
                    save = input(
                        "\n💾 Save all results to JSON? (y/n): ").strip().lower()
                    if save == "y":
                        save_test_results(
                            {"detective": result1, "cto": result2, "ghostwriter": result3, "complete_pipeline": result4}, username)

        elif choice == "7":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    main()
