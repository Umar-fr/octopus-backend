import json
from fastapi import APIRouter, HTTPException
from app.utils.db import SessionLocal
from app.models.issue import Issue
from app.models.solution import IssueSolution
from app.services.solution_generator import generate_solution
from app.services.solution_service import save_solution

router = APIRouter(prefix="/solutions", tags=["Solutions"])

@router.get("/{issue_id}")
def get_or_generate_solution(issue_id: int):
    db = SessionLocal()

    try:
        # 1️⃣ Check cache
        cached = (
            db.query(IssueSolution)
            .filter(IssueSolution.issue_id == issue_id)
            .first()
        )

        if cached:
            return {
                "cached": True,
                "steps": json.loads(cached.steps)
            }

        # 2️⃣ Load issue
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        # 3️⃣ Repo context (can be expanded later)
        repo_context = f"Repository ID: {issue.repo_id}"

        # 4️⃣ Generate solution (SAFE)
        try:
            steps = generate_solution(repo_context, issue)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "AI failed to generate a valid solution",
                    "error": str(e)
                }
            )

        # 5️⃣ Save to DB
        save_solution(db, issue.id, steps)

        return {
            "cached": False,
            "steps": steps
        }

    finally:
        db.close()
