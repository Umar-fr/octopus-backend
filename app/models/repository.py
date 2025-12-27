from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    repo_url = Column(String, unique=True, index=True)
    name = Column(String)
    analyzed = Column(Boolean, default=False)
