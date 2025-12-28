def build_repo_context(repo):
    context = {
        "name": repo.full_name,
        "language": repo.language,
        "default_branch": repo.default_branch,
        "description": repo.description,
    }
    return context

#Later this will expand to:

#folder structure

#key files

#build tools