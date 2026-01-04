from sqlalchemy import Column, Integer, ForeignKey, Text
from app.models.base import Base

class StepFeedback(Base):
    __tablename__ = "step_feedback"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    step_number = Column(Integer)
    user_error = Column(Text)
