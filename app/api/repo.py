from fastapi import APIRouter
from app.services.github_service import GitHubService
from app.services.repo_analyzer import analyze_repo
from app.services.issue_ingestor import ingest_issues
from app.utils.db import SessionLocal
from app.config.settings import settings
from sqlalchemy import text
from app.models.repository import Repository

router = APIRouter()

@router.post("/analyze")
def analyze_repository(repo_url: str):
    github = GitHubService(settings.GITHUB_TOKEN)
    repo = github.get_repo(repo_url)

    db = SessionLocal()

    try:
        # 1️⃣ Check if repo already exists (USE html_url)
        existing_repo = db.query(Repository).filter(
            Repository.repo_url == repo.html_url
        ).first()

        if existing_repo:
            repo_id = existing_repo.id
        else:
            # 2️⃣ Create new repo
            new_repo = Repository(
                repo_url=repo.html_url,
                name=repo.full_name,
                analyzed=True,
                github_id=repo.id
            )

            db.add(new_repo)
            db.commit()
            db.refresh(new_repo)

            repo_id = new_repo.id

        # 3️⃣ Ingest issues (SAFE to call multiple times)
        count = ingest_issues(repo, db, repo_id=repo_id)

        return {
            "repo": {
                "id": repo_id,
                "name": repo.full_name
            },
            "repo_id": repo_id,
            "issues_ingested": count
        }

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


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
