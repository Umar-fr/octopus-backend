def build_repo_context(repo, readme: str, tree: list[str]) -> str:
    context = f"""
Repository Name: {repo.owner.login}/{repo.name}
Primary Language: {repo.language}
Default Branch: {repo.default_branch}

Project Structure:
{chr(10).join(tree)}

README:
{readme[:4000]}
"""
    return context
