from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.api.repo import get_db
from app.auth.dependencies import get_current_user
from app.models.issue import Issue
from app.models.user_repository import UserRepository
from app.models.user import User

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.get("")
def get_issues(
    repo_id: int,
    difficulty: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 🔐 Access control
    allowed = db.query(UserRepository).filter(
        UserRepository.user_id == current_user.id,
        UserRepository.repository_id == repo_id,
    ).first()

    if not allowed:
        raise HTTPException(status_code=403, detail="Access denied")

    # 📦 Fetch issues
    query = db.query(Issue).filter(Issue.repo_id == repo_id)

    if difficulty:
        query = query.filter(Issue.difficulty == difficulty)

    issues = query.order_by(Issue.issue_number.asc()).all()

    # ✅ EXPLICIT RESPONSE SHAPE (CRITICAL FIX)
    return [
        {
            "id": issue.id,                       # internal DB id
            "issue_number": issue.issue_number,   # ✅ GitHub issue number
            "title": issue.title,
            "body": issue.body,
            "difficulty": issue.difficulty,
        }
        for issue in issues
    ]
