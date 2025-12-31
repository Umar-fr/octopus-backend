from sqlalchemy import Column, Integer, ForeignKey, Text
from app.models.base import Base

class IssueSolution(Base):
    __tablename__ = "issue_solutions"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), unique=True, index=True)
    steps = Column(Text)  # JSON string
