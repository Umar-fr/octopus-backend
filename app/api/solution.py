from fastapi import APIRouter
from app.services.solution_generator import generate_solution
from app.services.solution_service import save_solution
from app.services.repo_context import build_repo_context
from app.utils.db import SessionLocal
from app.models.issue import Issue

router = APIRouter()

@router.post("/solution/{issue_id}")
def solve_issue(issue_id: int):
    db = SessionLocal()

    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    repo = db.query(Repository).filter(Repository.id == issue.repo_id).first()

    repo_context = build_repo_context(repo)
    steps = generate_solution(repo_context, issue)

    save_solution(db, issue_id, steps)

    return {"steps": steps}
