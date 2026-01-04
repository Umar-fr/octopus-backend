from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.models.base import Base

class UserRepository(Base):
    __tablename__ = "user_repositories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), index=True)

    __table_args__ = (
        UniqueConstraint("user_id", "repository_id", name="uq_user_repo"),
    )
