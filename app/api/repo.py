from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    BackgroundTasks,
)
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import threading
import time
import traceback
import asyncio

from app.utils.db import SessionLocal
from app.config.settings import settings
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.repository import Repository
from app.models.issue import Issue
from app.models.user_repository import UserRepository

from app.services.github_service import GitHubService
from app.services.issue_ingestor import ingest_issues_chunked
from app.services.pending_issue_classifier import classify_pending_issues
from app.ws.progress_manager import repo_progress_manager


router = APIRouter()


# -------------------------
# DB Dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# SAFE WS BROADCAST (THREAD-SAFE)
# -------------------------
def ws_broadcast(repo_id: int, payload: dict):
    try:
        asyncio.run(
            repo_progress_manager.broadcast(repo_id, payload)
        )
    except RuntimeError:
        # happens if event loop already closed → ignore safely
        pass


# -------------------------
# Background Classifier
# -------------------------
def background_classifier(repo_id: int):
    db = SessionLocal()
    try:
        repo = db.query(Repository).get(repo_id)
        if not repo:
            return

        while True:
            processed = classify_pending_issues(db, repo_id)
            if processed == 0:
                break

            repo.issues_classified += processed
            db.commit()

            ws_broadcast(repo_id, {
                "issues_classified": repo.issues_classified,
                "issues_ingested": repo.issues_ingested,
                "issues_total_estimate": repo.issues_total_estimate,
                "status": "classifying",
            })

            time.sleep(1)

        repo.status = "ready"
        repo.analysis_stage = "complete"
        db.commit()

        ws_broadcast(repo_id, {
            "issues_classified": repo.issues_classified,
            "issues_ingested": repo.issues_ingested,
            "issues_total_estimate": repo.issues_total_estimate,
            "status": "ready",
        })

    finally:
        db.close()


# -------------------------
# Background Snapshot Ingest
# -------------------------
def analyze_repo_background(
    repo_id: int,
    repo_url: str,
    encrypted_github_token: str,  # ✅ NEW
):
    db = SessionLocal()
    repo = None  # ✅ IMPORTANT

    try:
        # ✅ Use USER token (encrypted)
        github = GitHubService(encrypted_github_token)
        gh_repo = github.get_repo(repo_url)

        repo = db.query(Repository).get(repo_id)
        if not repo:
            return

        repo.issues_ingested = 0
        repo.issues_classified = 0
        repo.status = "processing"
        repo.analysis_stage = "streaming"
        db.commit()

        ingest_issues_chunked(gh_repo, db, repo_id)

        # 🚫 If no issues were ingested
        if repo.issues_ingested == 0:
            repo.status = "ready"
            repo.analysis_stage = "no_issues"
        else:
            repo.status = "ready"
            repo.analysis_stage = "complete"

        db.commit()

    except Exception:
        if repo:  # ✅ avoid UnboundLocalError
            repo.status = "error"
            repo.analysis_stage = "error"
            db.commit()
        traceback.print_exc()

    finally:
        db.close()



# -------------------------
# ANALYZE ENDPOINT
# -------------------------
@router.post("/analyze")
def analyze_repository(
    repo_url: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ✅ user token is encrypted, GitHubService decrypts internally
    github = GitHubService(current_user.github_token)
    gh_repo = github.get_repo(repo_url)

    # 🔍 CHECK IF REPO HAS ISSUES ENABLED / AVAILABLE
    open_issues = github.get_open_issue_count(
        gh_repo.owner.login,
        gh_repo.name,
    )

    repo = (
        db.query(Repository)
        .filter(Repository.github_id == gh_repo.id)
        .first()
    )

    if not repo:
        # 🚫 NO ISSUES CASE
        if open_issues == 0:
            repo = Repository(
                github_id=gh_repo.id,
                name=gh_repo.name,
                owner=gh_repo.owner.login,
                repo_url=gh_repo.html_url,
                status="ready",
                analysis_stage="no_issues",
                issues_total_estimate=0,
            )
            db.add(repo)
            db.commit()
            db.refresh(repo)

        # ✅ NORMAL FLOW
        else:
            repo = Repository(
                github_id=gh_repo.id,
                name=gh_repo.name,
                owner=gh_repo.owner.login,
                repo_url=gh_repo.html_url,
                status="queued",
                analysis_stage="queued",
                issues_total_estimate=open_issues,
            )
            db.add(repo)
            db.commit()
            db.refresh(repo)

            background_tasks.add_task(
                analyze_repo_background,
                repo.id,
                repo_url,
                current_user.github_token,
            )

    exists = (
        db.query(UserRepository)
        .filter_by(
            user_id=current_user.id,
            repository_id=repo.id,
        )
        .first()
    )

    if not exists:
        db.add(
            UserRepository(
                user_id=current_user.id,
                repository_id=repo.id,
            )
        )
        db.commit()

    return {
        "repo_id": repo.id,
        "repo": f"{repo.owner}/{repo.name}",
        "status": repo.status,
    }


# -------------------------
# REPOSITORIES (SAFE FALLBACK)
# -------------------------
@router.get("/repositories")
def get_repositories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repos = (
        db.query(Repository)
        .join(UserRepository)
        .filter(UserRepository.user_id == current_user.id)
        .order_by(Repository.id.desc())
        .all()
    )

    response = []

    for r in repos:
        ingested = (
            db.query(func.count(Issue.id))
            .filter(Issue.repo_id == r.id)
            .scalar()
        )

        classified = (
            db.query(func.count(Issue.id))
            .filter(
                Issue.repo_id == r.id,
                Issue.difficulty != "Pending"
            )
            .scalar()
        )

        total = max(r.issues_total_estimate or 0, ingested)
        completion = int((classified / total) * 100) if total else 0

        response.append({
            "id": r.id,
            "name": f"{r.owner}/{r.name}",
            "status": r.status,
            "analysis_stage": r.analysis_stage,
            "issues_ingested": ingested,
            "issues_classified": classified,
            "issues_total_estimate": total,
            "completion": completion,
        })

    return response


# -------------------------
# DELETE
# -------------------------
@router.delete("/repositories/{repo_id}")
def delete_repository(
    repo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = (
        db.query(UserRepository)
        .filter_by(
            user_id=current_user.id,
            repository_id=repo_id,
        )
        .first()
    )

    if not link:
        raise HTTPException(status_code=404, detail="Repository not found")

    db.delete(link)
    db.commit()

    still_used = (
        db.query(UserRepository)
        .filter_by(repository_id=repo_id)
        .count()
    )

    if still_used == 0:
        repo = db.query(Repository).get(repo_id)
        if repo:
            db.delete(repo)
            db.commit()

    return {"status": "deleted"}


# -------------------------
# HEALTH
# -------------------------
@router.get("/health/db")
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "connected"}
