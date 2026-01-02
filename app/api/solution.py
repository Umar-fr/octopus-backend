import json
from fastapi import APIRouter, HTTPException
from app.utils.db import SessionLocal
from app.models.issue import Issue
from app.models.solution import IssueSolution
from app.services.solution_generator import generate_solution
from app.services.solution_service import save_solution
from app.services.github_service import GitHubService
from app.services.repo_context_builder import build_repo_context
from app.config.settings import settings
from app.models.repository import Repository

router = APIRouter(prefix="/solutions", tags=["Solutions"])

@router.get("/{issue_id}")
def get_or_generate_solution(issue_id: int):
    db = SessionLocal()

    try:
        cached = db.query(IssueSolution).filter_by(issue_id=issue_id).first()
        if cached:
            return {"cached": True, "steps": json.loads(cached.steps)}

        issue = db.query(Issue).filter_by(id=issue_id).first()
        if not issue:
            raise HTTPException(404, "Issue not found")

        repo = db.query(Repository).filter_by(id=issue.repo_id).first()
        if not repo:
            raise HTTPException(404, "Repository not found")

        github = GitHubService(settings.GITHUB_TOKEN)
        gh_repo = github.client.get_repo(f"{repo.owner}/{repo.name}")

        readme = github.get_readme(gh_repo)
        tree = github.get_tree(gh_repo)

        repo_context = build_repo_context(gh_repo, readme, tree)

        steps = generate_solution(repo_context, issue)

        save_solution(db, issue.id, steps)

        return {"cached": False, "steps": steps}

    finally:
        db.close()
