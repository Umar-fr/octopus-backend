from app.services.difficulty_classifier import classify_issue
from app.models.issue import Issue

def ingest_issues_chunked(repo, db, repo_id):
    per_page = 100
    page = 1
    total_ingested = 0

    while True:
        issues = repo.get_issues(
            state="open",
            per_page=per_page,
            page=page
        )

        if issues.totalCount == 0:
            break

        for issue in issues:
            if issue.pull_request:
                continue

            # skip if already exists
            exists = db.query(Issue).filter(
                Issue.repo_id == repo_id,
                Issue.issue_number == issue.number
            ).first()
            if exists:
                continue

            difficulty = classify_issue(issue)  # AI call

            db_issue = Issue(
                repo_id=repo_id,
                issue_number=issue.number,
                title=issue.title,
                body=issue.body or "",
                difficulty=difficulty
            )
            db.add(db_issue)

        db.commit()
        total_ingested += len(issues)
        page += 1

    return total_ingested

