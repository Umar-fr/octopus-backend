@router.post("/feedback")
def submit_feedback(issue_id: int, step_number: int, error: str):
    db = SessionLocal()

    feedback = StepFeedback(
        issue_id=issue_id,
        step_number=step_number,
        user_error=error
    )
    db.add(feedback)
    db.commit()

    return {"status": "received"}
