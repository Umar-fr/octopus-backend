from app.utils.db import engine
from app.models.base import Base

# IMPORTANT: import models so SQLAlchemy knows them
from app.models.issue import Issue
from app.models.repository import Repository
from app.models.solution import IssueSolution
from app.models.feedback import StepFeedback
from app.models.user_repository import UserRepository
from app.models.user import User
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
