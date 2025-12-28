from sqlalchemy import Column, Integer, Text
from app.models.base import Base

class StepFeedback(Base):
    __tablename__ = "step_feedback"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer)
    step_number = Column(Integer)
    user_error = Column(Text)
