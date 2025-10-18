import os
import json
import requests

class GitHubHelper:
    """GitHub helper: fetch issues, comments, and post comments.
       Includes a local triage cache to avoid duplicate comments.
    """

    def __init__(self, repo: str, token: str, cache_file: str = "triaged.json"):
        self.repo = repo
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json"
        }
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                return json.load(open(self.cache_file, "r"))
            except Exception:
                return {"triaged": []}
        return {"triaged": []}

    def _save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)

    def fetch_incident_issues(self):
        url = f"https://api.github.com/repos/{self.repo}/issues?labels=incident&state=open"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def _get_comments(self, issue_number: int):
        url = f"https://api.github.com/repos/{self.repo}/issues/{issue_number}/comments"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def comment_issue_once(self, issue_number: int, body: str):
        """Post comment only once: checks cache and existing comments."""
        issue_key = f"issue-{issue_number}"
        if issue_key in self.cache["triaged"]:
            print(f"Skipping #{issue_number}: already in local cache.")
            return False

        comments = self._get_comments(issue_number)
        if any("Agentic L1/L2 Triage Summary" in c["body"] for c in comments):
            print(f"Skipping #{issue_number}: triage comment already exists on GitHub.")
            self.cache["triaged"].append(issue_key)
            self._save_cache()
            return False

        url = f"https://api.github.com/repos/{self.repo}/issues/{issue_number}/comments"
        r = requests.post(url, headers=self.headers, json={"body": body})
        if r.status_code >= 400:
            print(f"Failed to post comment on #{issue_number}: {r.status_code} {r.text}")
            return False

        self.cache["triaged"].append(issue_key)
        self._save_cache()
        print(f"Posted triage comment on #{issue_number}")
        return True
