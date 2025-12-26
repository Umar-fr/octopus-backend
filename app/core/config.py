import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Octopus Backend")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ('true', '1', 't')
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else []