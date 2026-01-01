from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    owner = Column(String, index=True)
    repo_url = Column(String)

    analyzed = Column(Boolean, default=False)
    status = Column(String, default="idle")  
    # idle | analyzing | ready | empty | error