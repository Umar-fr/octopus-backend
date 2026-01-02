from sqlalchemy import Column, Integer, String, Text
from app.models.base import Base

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, index=True)
    issue_number = Column(Integer, nullable=False)
    title = Column(String)
    body = Column(Text)
    difficulty = Column(String)  # Beginner | Moderate | Professional
