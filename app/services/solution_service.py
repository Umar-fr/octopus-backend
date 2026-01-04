import json
from app.models.solution import IssueSolution

def save_solution(db, issue_id, steps):
    existing = (
        db.query(IssueSolution)
        .filter(IssueSolution.issue_id == issue_id)
        .first()
    )

    if existing:
        return existing

    solution = IssueSolution(
        issue_id=issue_id,
        steps=json.dumps(steps)
    )
    db.add(solution)
    db.commit()
    db.refresh(solution)
    return solution
