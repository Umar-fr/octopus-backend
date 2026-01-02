from github import Github
from typing import List
import base64

class GitHubService:
    def __init__(self, token: str):
        self.client = Github(token)

    def get_repo(self, repo_url: str):
        parts = repo_url.replace("https://github.com/", "").split("/")
        owner, repo = parts[0], parts[1]
        return self.client.get_repo(f"{owner}/{repo}")

    def get_readme(self, repo) -> str:
        try:
            readme = repo.get_readme()
            return base64.b64decode(readme.content).decode("utf-8")
        except Exception:
            return ""

    def get_tree(self, repo, max_items=50) -> List[str]:
        """
        Token-safe repo structure extraction
        """
        tree = repo.get_git_tree(repo.default_branch, recursive=True).tree
        paths = []

        for item in tree:
            if len(paths) >= max_items:
                break
            if item.type == "tree":
                paths.append(f"{item.path}/")

        return paths
