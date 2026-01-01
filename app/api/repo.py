from fastapi import APIRouter, HTTPException, Query, Depends
from app.services.github_service import GitHubService
from app.services.issue_ingestor import ingest_issues
from app.utils.db import SessionLocal
from app.config.settings import settings
from app.models.repository import Repository
from app.models.issue import Issue
from sqlalchemy import text, func
from sqlalchemy.orm import Session

router = APIRouter()


# -------------------------
# Utility: DB Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# ANALYZE REPOSITORY
# -------------------------
@router.post("/analyze")
def analyze_repository(
    repo_url: str,
    force: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    github = GitHubService(settings.GITHUB_TOKEN)
    repo = github.get_repo(repo_url)

    db_repo = (
        db.query(Repository)
        .filter(
            Repository.name == repo.name,
            Repository.owner == repo.owner.login
        )
        .first()
    )

    if not db_repo:
        db_repo = Repository(
            github_id=repo.id,
            name=repo.name,
            owner=repo.owner.login,
            repo_url=repo.html_url,
            status="analyzing",
            analyzed=False
        )
        db.add(db_repo)
        db.commit()
        db.refresh(db_repo)

    # 🔥 FORCE REANALYZE (delete issues only, repo stays)
    if force:
        db.query(Issue).filter(Issue.repo_id == db_repo.id).delete()
        db.commit()

    issue_count = (
        db.query(func.count(Issue.id))
        .filter(Issue.repo_id == db_repo.id)
        .scalar()
    )

    if issue_count == 0:
        db_repo.status = "analyzing"
        db.commit()

        try:
            count = ingest_issues(repo, db, repo_id=db_repo.id)

            db_repo.status = "ready" if count > 0 else "empty"
            db_repo.analyzed = True
            db.commit()

        except Exception as e:
            db_repo.status = "error"
            db.commit()
            raise HTTPException(status_code=500, detail=str(e))

    return {
        "repo_id": db_repo.id,
        "repo": f"{db_repo.owner}/{db_repo.name}",
        "status": db_repo.status
    }


# -------------------------
# GET ALL REPOSITORIES
# -------------------------
@router.get("/repositories")
def get_repositories(db: Session = Depends(get_db)):
    repos = db.query(Repository).order_by(Repository.id.desc()).all()
    return [
        {
            "id": r.id,
            "name": f"{r.owner}/{r.name}",
            "status": r.status
        }
        for r in repos
    ]


# -------------------------
# DELETE REPOSITORY (🔥 NEW)
# -------------------------
@router.delete("/repositories/{repo_id}")
def delete_repository(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # 🚨 This will automatically delete:
    # - issues
    # - solutions (via cascade)
    db.delete(repo)
    db.commit()

    return {"message": "Repository and related data deleted successfully"}


# -------------------------
# DB HEALTH CHECK
# -------------------------
@router.get("/health/db")
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "connected"}
