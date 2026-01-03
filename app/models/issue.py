from sqlalchemy import Column, Integer, String, Text, Index
from app.models.base import Base

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, index=True)
    issue_number = Column(Integer, nullable=False)
    title = Column(String)
    body = Column(Text)

    # 👇 NEW
    difficulty = Column(String, default="Pending", index=True)

    __table_args__ = (
        Index("idx_repo_difficulty", "repo_id", "difficulty"),
    )
