from sqlalchemy import Column, Integer, Text, ForeignKey
from app.models.base import Base

class IssueSolution(Base):
    __tablename__ = "issue_solutions"

    id = Column(Integer, primary_key=True)
    issue_id = Column(
        Integer,
        ForeignKey("issues.id", ondelete="CASCADE"),
        nullable=False,
        unique=True  # ✅ ONE solution per issue (GLOBAL)
    )
    steps = Column(Text, nullable=False)
