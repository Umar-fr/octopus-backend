from app.models.issue import Issue
from app.models.repository import Repository
from sqlalchemy.orm import Session
from app.ws.progress_manager import repo_progress_manager
from app.services.difficulty_classifier import classify_issue
import threading
import asyncio


def ws_broadcast_threadsafe(repo_id: int, payload: dict):
    """
    Safe WS broadcast from non-async threads
    """
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(repo_progress_manager.broadcast(repo_id, payload))
    except RuntimeError:
        # no event loop → create one just for this broadcast
        asyncio.run(repo_progress_manager.broadcast(repo_id, payload))


def ingest_issues_chunked(repo, db: Session, repo_id: int):
    db_repo = db.query(Repository).get(repo_id)
    if not db_repo:
        return

    issues = repo.get_issues(state="open")

    for gh_issue in issues:
        if gh_issue.pull_request:
            continue

        exists = db.query(Issue).filter(
            Issue.repo_id == repo_id,
            Issue.issue_number == gh_issue.number
        ).first()

        if exists:
            continue

        issue = Issue(
            repo_id=repo_id,
            issue_number=gh_issue.number,
            title=gh_issue.title,
            body=gh_issue.body or "",
            difficulty="Pending"
        )

        db.add(issue)
        db.commit()

        # ✅ INGESTED
        db_repo.issues_ingested += 1
        db.commit()

        ws_broadcast_threadsafe(repo_id, {
            "issues_ingested": db_repo.issues_ingested,
        })

        # 🔥 CLASSIFY IMMEDIATELY (PIPELINED)
        try:
            issue.difficulty = classify_issue(issue.title, issue.body)
            db_repo.issues_classified += 1
            db.commit()

            ws_broadcast_threadsafe(repo_id, {
                "issues_classified": db_repo.issues_classified,
            })

        except Exception:
            # stays Pending, retried later if needed
            db.commit()
