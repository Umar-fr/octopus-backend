from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Depends,
    BackgroundTasks
)
from app.services.github_service import GitHubService
from app.services.issue_ingestor import ingest_issues_chunked
from app.utils.db import SessionLocal
from app.config.settings import settings
from app.models.repository import Repository
from app.models.issue import Issue
from sqlalchemy import text
from sqlalchemy.orm import Session
import traceback
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def analyze_repo_background(repo_id: int, repo_url: str, force: bool):
    db = SessionLocal()
    try:
        github = GitHubService(settings.GITHUB_TOKEN)
        repo = github.get_repo(repo_url)

        db_repo = db.query(Repository).get(repo_id)
        if not db_repo:
            return

        if force:
            db.query(Issue).filter(Issue.repo_id == repo_id).delete()
            db.commit()

        db_repo.status = "analyzing"
        db.commit()

        count = ingest_issues_chunked(repo, db, repo_id)

        db_repo.status = "ready" if count > 0 else "empty"
        db_repo.analyzed = True
        db.commit()

    except Exception as e:
        print("❌ ANALYZE FAILED")
        print(traceback.format_exc())

        db_repo = db.query(Repository).get(repo_id)
        if db_repo:
            db_repo.status = "error"
            db.commit()
    finally:
        db.close()


from app.models.user_repository import UserRepository

@router.post("/analyze")
def analyze_repository(
    repo_url: str,
    background_tasks: BackgroundTasks,
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    github = GitHubService(settings.GITHUB_TOKEN)
    repo = github.get_repo(repo_url)

    # GLOBAL repo lookup
    db_repo = db.query(Repository).filter(
        Repository.github_id == repo.id
    ).first()

    if not db_repo:
        db_repo = Repository(
            github_id=repo.id,
            name=repo.name,
            owner=repo.owner.login,
            repo_url=repo.html_url,
            status="queued",
            analyzed=False
        )
        db.add(db_repo)
        db.commit()
        db.refresh(db_repo)

        background_tasks.add_task(
            analyze_repo_background,
            db_repo.id,
            repo_url,
            force
        )

    # LINK USER TO REPO
    exists = db.query(UserRepository).filter(
        UserRepository.user_id == current_user["id"],
        UserRepository.repository_id == db_repo.id
    ).first()

    if not exists:
        db.add(UserRepository(
            user_id=current_user["id"],
            repository_id=db_repo.id
        ))
        db.commit()

    return {
        "repo_id": db_repo.id,
        "repo": f"{db_repo.owner}/{db_repo.name}",
        "status": db_repo.status
    }



@router.get("/repositories")
def get_repositories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repos = (
        db.query(Repository)
        .join(UserRepository)
        .filter(UserRepository.user_id == current_user.id)
        .order_by(Repository.id.asc())
        .all()
    )

    return [
        {
            "id": r.id,
            "name": f"{r.owner}/{r.name}",
            "status": r.status
        }
        for r in repos
    ]



@router.delete("/repositories/{repo_id}")
def delete_repository(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    db.delete(repo)
    db.commit()
    return {"message": "Repository deleted"}


@router.get("/health/db")
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "connected"}
