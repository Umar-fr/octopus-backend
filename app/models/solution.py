from sqlalchemy import Column, Integer, ForeignKey, Text, UniqueConstraint
from app.models.base import Base

class IssueSolution(Base):
    __tablename__ = "issue_solutions"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    steps = Column(Text)

    __table_args__ = (
        UniqueConstraint("issue_id", "user_id", name="uq_issue_solution_user"),
    )
