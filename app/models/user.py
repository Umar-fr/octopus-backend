from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    github_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, index=True)
    # idle | analyzing | ready | empty | error