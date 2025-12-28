from fastapi import APIRouter
from app.services.github_service import GitHubService
from app.services.repo_analyzer import analyze_repo
from app.services.issue_ingestor import ingest_issues
from app.utils.db import SessionLocal
from app.config.settings import settings
from sqlalchemy import text

router = APIRouter()

@router.post("/analyze")
def analyze_repository(repo_url: str):
    github = GitHubService(settings.GITHUB_TOKEN)
    repo = github.get_repo(repo_url)

    db = SessionLocal()
    repo_data = analyze_repo(repo)
    issue=repo.get_issues(state="open")
    for issues in issue:
        print(issues.title)

    # save repo & issues (simplified)
    count = ingest_issues(repo, db, repo_id=1)

    return {
        "repo": repo_data,
        "issues_ingested": count,
        "db_connection": db.bind.url.__str__()
    }

@router.get("/health/db")
def db_health():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"db": "connected"}
    except Exception as e:
        return {"db": "error", "detail": str(e)}
    finally:
        db.close()
