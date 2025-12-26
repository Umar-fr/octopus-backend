from fastapi import APIRouter
from app.services.github_service import GitHubService
from app.services.repo_analyzer import analyze_repo
from app.services.issue_ingestor import ingest_issues
from app.utils.db import SessionLocal
from app.config.settings import settings

router = APIRouter()

@router.post("/analyze")
def analyze_repository(repo_url: str):
    github = GitHubService(settings.GITHUB_TOKEN)
    repo = github.get_repo(repo_url)

    db = SessionLocal()
    repo_data = analyze_repo(repo)

    # save repo & issues (simplified)
    count = ingest_issues(repo, db, repo_id=1)

    return {
        "repo": repo_data,
        "issues_ingested": count
    }
