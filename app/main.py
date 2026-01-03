from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.issues import router as issues_router
from app.auth.github import router as github_router
from app.api.repo import router as repo_router
from app.api.solution import router as solution_router
from app.api.feedback import router as feedback_router
from app.api.ws import router as ws_router


load_dotenv(".env.local")

app = FastAPI(title="Octopus Backend")

# ✅ ADD THIS BLOCK
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(github_router)
app.include_router(repo_router)
app.include_router(issues_router)
app.include_router(solution_router)
app.include_router(feedback_router)
app.include_router(ws_router)

@app.get("/")
def root():
    return {"status": "Backend running"}
