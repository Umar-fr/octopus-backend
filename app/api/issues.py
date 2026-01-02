from http.client import HTTPException
from fastapi import APIRouter, Depends, Query
from app.utils.db import SessionLocal
from app.models.issue import Issue
from app.models.user_repository import UserRepository
from app.models.repository import Repository
from app.api.repo import get_db
from app.auth.dependencies import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/issues", tags=["Issues"])



@router.get("")
def get_issues(
    repo_id: int,
    difficulty: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    allowed = db.query(UserRepository).filter(
        UserRepository.user_id == current_user["id"],
        UserRepository.repository_id == repo_id
    ).first()

    if not allowed:
        raise HTTPException(status_code=403, detail="Access denied")

    query = db.query(Issue).filter(Issue.repo_id == repo_id)

    if difficulty:
        query = query.filter(Issue.difficulty == difficulty)

    return query.order_by(Issue.id.asc()).all()
