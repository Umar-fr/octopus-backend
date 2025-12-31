from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)        # repo name only
    owner = Column(String, index=True)       # repo owner
    repo_url = Column(String)                # full GitHub URL
    analyzed = Column(Boolean, default=True)
