from app.models.issue import Issue
from sqlalchemy.orm import Session
from app.services.difficulty_classifier import classify_issue


def ingest_issues_chunked(repo, db: Session, repo_id: int) -> int:
    """
    PyGithub-safe, resume-safe issue ingestion
    """
    total_ingested = 0
    batch_size = 25
    batch_counter = 0

    issues = repo.get_issues(state="open")

    for issue in issues:
        if issue.pull_request:
            continue

        exists = db.query(Issue).filter(
            Issue.repo_id == repo_id,
            Issue.issue_number == issue.number
        ).first()

        if exists:
            continue

        # ✅ FIXED CALL SIGNATURE
        difficulty = classify_issue(
            issue.title,
            issue.body or ""
        )

        db.add(
            Issue(
                repo_id=repo_id,
                issue_number=issue.number,
                title=issue.title,
                body=issue.body or "",
                difficulty=difficulty
            )
        )

        total_ingested += 1
        batch_counter += 1

        # Commit in small batches
        if batch_counter >= batch_size:
            db.commit()
            batch_counter = 0

    if batch_counter > 0:
        db.commit()

    return total_ingested
