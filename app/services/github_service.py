from github import Github
from typing import List, Dict

class GitHubService:
    def __init__(self, token: str):
        self.client = Github(token)

    def get_repo(self, repo_url: str):
        # repo_url: https://github.com/owner/repo
        parts = repo_url.replace("https://github.com/", "").split("/")
        owner, repo = parts[0], parts[1]
        return self.client.get_repo(f"{owner}/{repo}")

    def get_issues(self, repo, state="open"):
        return repo.get_issues(state=state)
