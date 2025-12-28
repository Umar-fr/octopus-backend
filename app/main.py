from fastapi import FastAPI
from dotenv import load_dotenv
from app.auth.github import router as github_router
from app.api.repo import router as repo_router

load_dotenv(".env.local")

app = FastAPI(title="Octopus Backend")

app.include_router(github_router)
app.include_router(repo_router)

@app.get("/")
def root():
    return {"status": "Backend running"}
