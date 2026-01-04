from github import Github
from typing import List
import base64
from app.utils.crypto import decrypt

class GitHubService:
    def __init__(self, encrypted_token: str):
        if not encrypted_token:
            raise ValueError("Missing GitHub token")

        token = decrypt(encrypted_token)
        self.client = Github(token, per_page=100)

    def get_repo(self, repo_url: str):
        parts = repo_url.replace("https://github.com/", "").strip("/").split("/")
        owner, repo = parts[0], parts[1]
        return self.client.get_repo(f"{owner}/{repo}")

    def get_readme(self, repo) -> str:
        try:
            readme = repo.get_readme()
            return base64.b64decode(readme.content).decode("utf-8")
        except Exception:
            return ""

    def get_tree(self, repo, max_items=800) -> List[str]:
        tree = repo.get_git_tree(repo.default_branch, recursive=True).tree
        paths = []

        for item in tree:
            if len(paths) >= max_items:
                break

            if item.type == "tree":
                paths.append(f"{item.path}/")
            elif item.type == "blob":
                paths.append(item.path)

        return paths

    def get_file_content(self, repo, path: str) -> str:
        try:
            file = repo.get_contents(path)
            if file.encoding == "base64":
                return base64.b64decode(file.content).decode("utf-8")
            return ""
        except Exception:
            return ""

    def get_open_issue_count(self, owner: str, repo: str) -> int:
        """
        TRUE open issues count (PRs excluded)
        """
        query = f"repo:{owner}/{repo} is:issue is:open"
        return self.client.search_issues(query=query).totalCount
