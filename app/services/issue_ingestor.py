from app.services.difficulty_classifier import classify_issue
from app.models.issue import Issue

def ingest_issues(repo, db, repo_id):
    issues = repo.get_issues(state="open")
    count = 0

    for issue in issues:
        # ✅ Correct PR filtering
        if issue.pull_request is not None:
            continue

        difficulty = classify_issue(issue.title, issue.body or "")

        db_issue = Issue(
            repo_id=repo_id,
            issue_number=issue.number,
            title=issue.title,
            body=issue.body or "",
            difficulty=difficulty
        )

        db.add(db_issue)
        count += 1

    db.commit()
    return count
