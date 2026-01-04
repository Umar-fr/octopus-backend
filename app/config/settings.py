import os
from dotenv import load_dotenv

load_dotenv(".env.local")


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    GITHUB_TOKEN_SECRET: str = os.getenv("GITHUB_TOKEN_SECRET", "")


settings = Settings()
