from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.issue import Issue
from app.models.solution import IssueSolution
from app.models.feedback import StepFeedback
from app.services.solution_generator import generate_solution
from app.services.feedback_solver import refine_solution
from app.services.solution_validator import enforce_strict_paths
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
    db: Session = SessionLocal()

    try:
        # 1️⃣ Load issue + repo
        issue = db.query(Issue).filter_by(id=issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        repo = db.query(Repository).filter_by(id=issue.repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

        # 2️⃣ Load GitHub context (ALWAYS)
        github = GitHubService(settings.GITHUB_TOKEN)
        gh_repo = github.client.get_repo(f"{repo.owner}/{repo.name}")

        readme = github.get_readme(gh_repo)
        tree = github.get_tree(gh_repo)

        repo_context = build_repo_context(gh_repo, readme, tree)

        # 3️⃣ Load or generate GLOBAL solution
        solution = (
            db.query(IssueSolution)
            .filter(IssueSolution.issue_id == issue_id)
            .first()
        )

        if not solution:
            steps = generate_solution(repo_context, issue)

            # 🔒 Enforce strict repo accuracy BEFORE saving
            steps = enforce_strict_paths(steps, tree)

            # 🔒 Ensure PR step exists ONCE
            if not any("pull request" in s["title"].lower() for s in steps):
                steps.append({
                    "step": max(s["step"] for s in steps) + 1,
                    "title": "Open Pull Request",
                    "explanation": "Submit your changes for maintainer review.",
                    "file": "",
                    "action": (
                        "git push origin <your-branch>\n"
                        "Open GitHub → Create Pull Request"
                    ),
                    "verification": "CI passes and maintainers review the PR."
                })

            solution = IssueSolution(
                issue_id=issue_id,
                steps=json.dumps(steps)
            )
            db.add(solution)
            db.commit()

        else:
            steps = json.loads(solution.steps)

        # 4️⃣ Apply USER-SPECIFIC feedback (overlay only)
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
                repo_context=repo_context,
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