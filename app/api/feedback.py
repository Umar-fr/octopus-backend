from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.feedback import StepFeedback
from app.models.issue import Issue
from app.models.solution import IssueSolution
from app.services.feedback_solver import refine_solution
from app.auth.dependencies import get_current_user
from app.models.user import User
import json

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    issue_id: int
    step_number: int
    error: str


@router.post("")
def submit_feedback(
    payload: FeedbackRequest,
    current_user: User = Depends(get_current_user),
):
    db: Session = SessionLocal()

    try:
        # 1️⃣ Validate issue
        issue = db.query(Issue).filter_by(id=payload.issue_id).first()
        if not issue:
            raise HTTPException(404, "Issue not found")

        # 2️⃣ Validate solution exists
        solution = (
            db.query(IssueSolution)
            .filter(IssueSolution.issue_id == payload.issue_id)
            .first()
        )
        if not solution:
            raise HTTPException(400, "Solution not generated yet")

        steps = json.loads(solution.steps)

        failed_step = next(
            (s for s in steps if s["step"] == payload.step_number),
            None
        )
        if not failed_step:
            raise HTTPException(404, "Step not found")

        # 3️⃣ Generate refined step (DO NOT SAVE)
        try:
            refined_step = refine_solution(
                repo_context=f"Repository ID: {issue.repo_id}",
                issue=issue,
                step=failed_step,
                error=payload.error,
            )
        except Exception as e:
            # Fallback: return original step unchanged
            refined_step = failed_step

        # 4️⃣ Save feedback ONLY
        feedback = StepFeedback(
            issue_id=payload.issue_id,
            user_id=current_user.id,
            step_number=payload.step_number,
            user_error=payload.error,
        )
        db.add(feedback)
        db.commit()

        # 5️⃣ Return refined step ONLY to this user
        return {
            "status": "ok",
            "refined_step": refined_step
        }

    finally:
        db.close()
