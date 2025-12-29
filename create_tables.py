from app.utils.db import engine
from app.models.base import Base

# IMPORTANT: import models so SQLAlchemy knows them
from app.models.issue import Issue

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
