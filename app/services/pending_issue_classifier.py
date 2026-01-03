from sqlalchemy.orm import Session
from app.models.issue import Issue
from app.services.difficulty_classifier import classify_issue

CLASSIFY_BATCH = 25

def classify_pending_issues(db: Session, repo_id: int) -> int:
    pending = (
        db.query(Issue)
        .filter(
            Issue.repo_id == repo_id,
            Issue.difficulty == "Pending"
        )
        .order_by(Issue.issue_number.asc())
        .limit(CLASSIFY_BATCH)
        .with_for_update(skip_locked=True)  # 🔥 RETRY SAFE
        .all()
    )

    if not pending:
        return 0

    processed = 0

    for issue in pending:
        try:
            issue.difficulty = classify_issue(issue.title, issue.body or "")
            processed += 1
        except Exception:
            # leave as Pending → retried next loop
            continue

    db.commit()
    return processed
