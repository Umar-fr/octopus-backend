from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.services.github_service import GitHubService

router = APIRouter(prefix="/github", tags=["GitHub"])

@router.get("/repos")
def get_user_repositories(user=Depends(get_current_user)):
    service = GitHubService(user.github_token)

    repos = service.client.get_user().get_repos()

    result = []
    for repo in repos:
        result.append({
            "name": repo.name,
            "full_name": repo.full_name,
            "url": repo.html_url,
            "private": repo.private,
            "open_issues": repo.open_issues_count,
            "language": repo.language,
        })

    return result
