def build_repo_context(repo, readme: str, tree: list[str], files: dict[str, str]) -> str:
    file_blocks = []
    tree_preview = "\n".join(tree[:800])
    for path, content in files.items():
        file_blocks.append(
            f"\nFILE: {path}\n"
            f"{content[:3000]}"
        )

    context = f"""
You are working on a REAL GitHub repository.

Repository:
- Name: {repo.owner.login}/{repo.name}
- Primary Language: {repo.language}
- Default Branch: {repo.default_branch}

Project Structure:
{chr(10).join(tree)}

README:
{readme[:4000]}

IMPORTANT FILE CONTENTS:
{chr(10).join(file_blocks)}

IMPORTANT RULES:
- You may ONLY reference file paths that exist in the tree below
- If a file is not clearly present, say "Search required"
- Never invent file paths

Repository Tree (partial):
{tree_preview}

README (partial):
{readme[:4000]}

Contribution Expectations:
- Follow existing project structure
- Assume contributor uses a local dev environment
- Output steps suitable for a pull request
"""
    return context