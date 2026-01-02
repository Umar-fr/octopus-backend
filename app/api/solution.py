from fastapi import APIRouter, HTTPException, Depends
from app.utils.db import SessionLocal
from app.models.issue import Issue
from app.models.solution import IssueSolution
from app.models.feedback import StepFeedback
from app.services.solution_generator import generate_solution
from app.services.feedback_solver import refine_solution
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.repository import Repository
from app.services.github_service import GitHubService
from app.services.repo_context_builder import build_repo_context
from app.config.settings import settings
import json

router = APIRouter(prefix="/solutions", tags=["Solutions"])


@router.get("/{issue_id}")
def get_or_generate_solution(
    issue_id: int,
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        # 1️⃣ Load issue + repo
        issue = db.query(Issue).filter_by(id=issue_id).first()
        if not issue:
            raise HTTPException(404, "Issue not found")

        repo = db.query(Repository).filter_by(id=issue.repo_id).first()
        if not repo:
            raise HTTPException(404, "Repository not found")

        # 2️⃣ Get or generate GLOBAL solution
        solution = (
            db.query(IssueSolution)
            .filter(IssueSolution.issue_id == issue_id)
            .first()
        )

        if not solution:
            github = GitHubService(settings.GITHUB_TOKEN)
            gh_repo = github.client.get_repo(f"{repo.owner}/{repo.name}")

            readme = github.get_readme(gh_repo)
            tree = github.get_tree(gh_repo)

            repo_context = build_repo_context(gh_repo, readme, tree)
            steps = generate_solution(repo_context, issue)

            solution = IssueSolution(
                issue_id=issue_id,
                steps=json.dumps(steps)
            )
            db.add(solution)
            db.commit()
        else:
            steps = json.loads(solution.steps)

        # 3️⃣ Apply USER feedback dynamically
        feedbacks = (
            db.query(StepFeedback)
            .filter(
                StepFeedback.issue_id == issue_id,
                StepFeedback.user_id == current_user.id,
            )
            .all()
        )

        for fb in feedbacks:
            step = next(
                (s for s in steps if s["step"] == fb.step_number),
                None
            )
            if not step:
                continue

            refined = refine_solution(
                repo_context=f"Repository ID: {issue.repo_id}",
                issue=issue,
                step=step,
                error=fb.user_error,
            )

            for i, s in enumerate(steps):
                if s["step"] == fb.step_number:
                    steps[i] = refined
                    break

        return {
            "global": True,
            "steps": steps
        }

    finally:
        db.close()
