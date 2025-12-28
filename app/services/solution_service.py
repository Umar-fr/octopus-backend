import json
from app.models.solution import IssueSolution

def save_solution(db, issue_id, steps):
    solution = IssueSolution(
        issue_id=issue_id,
        steps=json.dumps(steps)
    )
    db.add(solution)
    db.commit()
