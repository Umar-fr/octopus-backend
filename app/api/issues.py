from fastapi import APIRouter, Query
from app.utils.db import SessionLocal
from app.models.issue import Issue

router = APIRouter(prefix="/issues", tags=["Issues"])

@router.get("/")
def get_issues(
    repo_id: int,
    difficulty: str | None = Query(default=None)
):
    db = SessionLocal()
    try:
        query = db.query(Issue).filter(Issue.repo_id == repo_id)

        if difficulty:
            query = query.filter(Issue.difficulty == difficulty)

        issues = query.order_by(Issue.id.desc()).all()

        return [
            {
                "id": i.id,
                "number": i.issue_number,
                "title": i.title,
                "body": i.body,
                "difficulty": i.difficulty
            }
            for i in issues
        ]
    finally:
        db.close()
