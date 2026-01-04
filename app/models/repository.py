from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True, index=True)
    name = Column(String)
    owner = Column(String)
    repo_url = Column(String)

    status = Column(String, default="queued")
    analysis_stage = Column(String, default="snapshot")

    issues_total_estimate = Column(Integer, default=0)
    issues_ingested = Column(Integer, default=0)
    issues_classified = Column(Integer, default=0)  # ✅ REQUIRED

    analyzed = Column(Boolean, default=False)
