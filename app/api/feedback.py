from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.feedback import StepFeedback
from app.models.issue import Issue
from app.models.solution import IssueSolution
from app.services.feedback_solver import refine_solution, regenerate_subsequent_steps
from app.auth.dependencies import get_current_user
from app.models.user import User
import json

router = APIRouter(prefix="/feedback", tags=["Feedback"])


# ✅ Request body schema
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
        # 1️⃣ Load issue
        issue = db.query(Issue).filter_by(id=payload.issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        # 2️⃣ Load existing solution
        solution = (
            db.query(IssueSolution)
            .filter(IssueSolution.issue_id == payload.issue_id)
            .first()
        )
        if not solution:
            raise HTTPException(
                status_code=400,
                detail="Solution does not exist yet"
            )

        steps = json.loads(solution.steps)

        # 3️⃣ Find the failed step
        failed_step = next(
            (s for s in steps if s["step"] == payload.step_number),
            None
        )
        if not failed_step:
            raise HTTPException(
                status_code=404,
                detail="Step not found in solution"
            )

        # 4️⃣ Refine the failed step using AI
        refined_step = refine_solution(
            repo_context=f"Repository ID: {issue.repo_id}",
            issue=issue,
            step=failed_step,
            error=payload.error,
        )

        # 5️⃣ Replace the refined step
        for i, s in enumerate(steps):
            if s["step"] == payload.step_number:
                steps[i] = refined_step
                break

        # 6️⃣ Regenerate all subsequent steps
        steps_before = [s for s in steps if s["step"] < payload.step_number]
        steps_after_index = payload.step_number  # Steps to regenerate start here
        
        # Get context: issue + all steps up to and including the refined one
        context_steps = steps[:payload.step_number]  # All steps before + the refined one
        
        new_subsequent_steps = regenerate_subsequent_steps(
            repo_context=f"Repository ID: {issue.repo_id}",
            issue=issue,
            completed_steps=context_steps,
            starting_step_number=payload.step_number + 1,
            total_steps=len(steps)  # Keep similar length, or make dynamic
        )

        # 7️⃣ Reconstruct the full solution
        steps = steps_before + [refined_step] + new_subsequent_steps

        # 8️⃣ Save feedback
        feedback = StepFeedback(
            issue_id=payload.issue_id,
            user_id=current_user.id,
            step_number=payload.step_number,
            user_error=payload.error,
        )
        db.add(feedback)

        # 9️⃣ Update solution
        solution.steps = json.dumps(steps)
        db.commit()

        return {
            "status": "refined",
            "refined_step": refined_step,
            "regenerated_steps": new_subsequent_steps,
            "total_steps": len(steps)
        }

    finally:
        db.close()