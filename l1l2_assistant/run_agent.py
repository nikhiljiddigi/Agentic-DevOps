import os
import time
from datetime import datetime

from l1l2_assistant import L1L2SupportAgent

# Poll interval in seconds
POLL_INTERVAL = int(os.getenv("AGENT_POLL_INTERVAL", "60"))  # default 1 minute
PROCESSED_FILE = ".processed_issues.txt"


def load_processed():
    """Load IDs of already processed issues."""
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r") as f:
        return {int(line.strip()) for line in f if line.strip().isdigit()}


def save_processed(processed):
    """Save IDs of processed issues."""
    with open(PROCESSED_FILE, "w") as f:
        for issue_id in processed:
            f.write(str(issue_id) + "\n")


def main():
    print("🤖 Starting Agentic L1/L2 Support Assistant (Continuous Mode)...")
    agent = L1L2SupportAgent()
    processed = load_processed()

    while True:
        try:
            print(f"\n⏱️ Checking for new incident issues at {datetime.utcnow().isoformat()}...")
            issues = agent.github.fetch_incident_issues()
            new_issues = [i for i in issues if i["number"] not in processed]

            if not new_issues:
                print("✅ No new incidents.")
            else:
                print(f"🚨 Found {len(new_issues)} new incident(s): {[i['number'] for i in new_issues]}")
                for issue in new_issues:
                    try:
                        agent.triage_issue(issue)
                        processed.add(issue["number"])
                    except Exception as e:
                        print(f"⚠️ Failed to triage issue #{issue['number']}: {e}")

                save_processed(processed)

        except Exception as e:
            print(f"⚠️ Agent loop error: {e}")

        print(f"🕒 Sleeping for {POLL_INTERVAL}s...\n")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
