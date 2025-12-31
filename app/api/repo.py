from fastapi import APIRouter
from app.services.github_service import GitHubService
from app.services.issue_ingestor import ingest_issues
from app.utils.db import SessionLocal
from app.config.settings import settings
from app.models.repository import Repository
from sqlalchemy import text

router = APIRouter()


@router.post("/analyze")
def analyze_repository(repo_url: str):
    github = GitHubService(settings.GITHUB_TOKEN)
    repo = github.get_repo(repo_url)

    db = SessionLocal()

    try:
        owner = repo.owner.login
        name = repo.name

        # ✅ Check if repo already exists
        existing_repo = (
            db.query(Repository)
            .filter(
                Repository.name == name,
                Repository.owner == owner
            )
            .first()
        )

        if not existing_repo:
            db_repo = Repository(
                github_id=repo.id,
                name=name,
                owner=owner,
                repo_url=repo.html_url,
                analyzed=True
            )
            db.add(db_repo)
            db.commit()
            db.refresh(db_repo)
        else:
            db_repo = existing_repo

        count = ingest_issues(repo, db, repo_id=db_repo.id)

        return {
            "repo": {
                "id": db_repo.id,
                "name": f"{db_repo.owner}/{db_repo.name}"
            },
            "repo_id": db_repo.id,
            "issues_ingested": count
        }

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()



@router.get("/repositories")
def get_repositories():
    db = SessionLocal()
    try:
        repos = db.query(Repository).order_by(Repository.id.desc()).all()
        return [
            {
                "id": r.id,
                # ✅ FIX
                "name": f"{r.owner}/{r.name}"
            }
            for r in repos
        ]
    finally:
        db.close()


@router.get("/health/db")
def db_health():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"db": "connected"}
    finally:
        db.close()
