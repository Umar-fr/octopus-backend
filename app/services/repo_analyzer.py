def analyze_repo(repo):
    return {
        "name": repo.full_name,
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "language": repo.language,
        "open_issues": repo.open_issues_count,
        "default_branch": repo.default_branch
    }
