"""
Agentic L1/L2 Support Assistant
-------------------------------
Run manually to triage open GitHub issues labeled as 'incident'.
Uses:
- Gemini 2.5 Flash (via DSPyHelper)
- KB lookup + similarity matching
- Duplicate detection
- Posts triage summary comment
"""

import os
from datetime import datetime

from utils.github_helper import GitHubHelper
from utils.similarity import find_relevant_kb
from utils.duplicate_detector import find_similar_issues
from utils.dspy_helper import DSPyHelper


# --------------------------------------------------------------------------- #
# Environment setup
# --------------------------------------------------------------------------- #

REPO = os.getenv("GITHUB_REPOSITORY") or "nikhiljiddigi/agentic-support-demo"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
KB_REPO = os.getenv("GITHUB_REPOSITORY") or "nikhiljiddigi/agentic-kb"

if not GITHUB_TOKEN:
    raise EnvironmentError("❌ Missing GITHUB_TOKEN (PAT with repo & issues permissions)")
if not REPO:
    raise EnvironmentError("❌ Missing GITHUB_REPOSITORY name")
if not KB_REPO:
    raise EnvironmentError("❌ Missing GITHUB_REPOSITORY name")

# --------------------------------------------------------------------------- #
# Agent definition
# --------------------------------------------------------------------------- #

class L1L2SupportAgent:
    """Agent that triages incident issues manually when invoked."""

    def __init__(self):
        self.github = GitHubHelper(REPO, GITHUB_TOKEN)
        self.reasoner = DSPyHelper()  # uses Gemini backend
        print(f"🔧 Initialized Agent for repo: {REPO}")

    # ---------------------------------------------------------------------- #
    def triage_issue(self, issue: dict):
        issue_number = issue["number"]
        title = issue["title"]
        body = issue.get("body", "")
        now = datetime.utcnow().isoformat()

        print(f"\n🚨 Processing incident #{issue_number}: {title}")

        # 1️⃣ Find KB article match
        kb_match = find_relevant_kb(body or title, KB_REPO, GITHUB_TOKEN)
        kb_text = kb_match.get("content", "No KB found")

        if kb_match and kb_match['score'] >= 0.75:
            kb_line = f"📘 KB: {kb_match['file']} (score: {kb_match['score']:.3f})"
        else:
            kb_line = ""

        # 2️⃣ Duplicate detection
        all_issues = self.github.fetch_incident_issues()
        duplicates = find_similar_issues(issue, all_issues, threshold=0.85)
        duplicate_section = ""
        if duplicates:
            dup_lines = [
                f"- [#{d['number']}](https://github.com/{REPO}/issues/{d['number']}): "
                f"{d['title']} (score {d['score']})"
                for d in duplicates
            ]
            duplicate_section = "\n\n🔁 **Similar Incidents:**\n" + "\n".join(dup_lines)

        # 3️⃣ L1/L2 triage reasoning
        fields = self.reasoner.run_reasoning(title, body, kb_text, now)

        # 4️⃣ Compose triage summary
        comment = f"""
### 🧠 Agentic L1/L2 Triage Summary
**Severity:** {fields.get('severity', 'N/A')}  
**Probable Cause:** {fields.get('probable_cause', 'N/A')}  
**Recommended Fix:** {fields.get('recommended_fix', 'N/A')}  
**Estimated Resolution Time:** {fields.get('resolution_time', 'N/A')}{duplicate_section}

{kb_line}
""".strip()

        # 5️⃣ Post once to GitHub
        self.github.comment_issue_once(issue_number, comment)
        print(f"✅ Triage posted for issue #{issue_number}")

    # ---------------------------------------------------------------------- #
    def run(self):
        """Manually run triage on all open incident issues."""
        issues = self.github.fetch_incident_issues()
        if not issues:
            print("✅ No open incident issues found.")
            return

        print(f"📋 Found {len(issues)} incident(s). Starting triage...\n")
        for issue in issues:
            if issue["number"] in self.github.cache.get("triaged", []):
                print(f"⚠️ Issue #{issue['number']} already triaged.")
                continue
            self.triage_issue(issue)


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #

def main():
    agent = L1L2SupportAgent()
    agent.run()


if __name__ == "__main__":
    main()
