import os
import requests
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from app.utils.jwt import create_access_token
from app.utils.db import SessionLocal
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


# 1️⃣ Redirect user to GitHub
@router.get("/github")
def github_login():
    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={os.getenv('GITHUB_CLIENT_ID')}"
        f"&redirect_uri={os.getenv('GITHUB_REDIRECT_URI')}"
        "&scope=user"
        "&prompt=select_account"
    )

    return RedirectResponse(github_auth_url)


# 2️⃣ GitHub callback
@router.get("/github/callback")
def github_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    # Exchange code → access token
    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "code": code,
            "redirect_uri": os.getenv("GITHUB_REDIRECT_URI"),
        },
    )

    access_token = token_response.json().get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="GitHub auth failed")

    # Fetch GitHub user
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    github_user = user_response.json()

    # 🔹 Create / fetch user
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            User.github_id == github_user["id"]
        ).first()

        if not user:
            user = User(
                github_id=github_user["id"],
                username=github_user["login"]
            )
            db.add(user)
            db.commit()
    finally:
        db.close()

    # 🔹 Create JWT
    jwt_token = create_access_token({
        "github_id": github_user["id"],
        "username": github_user["login"],
        "avatar": github_user["avatar_url"],
    })

    return RedirectResponse(
        f"{os.getenv('FRONTEND_URL')}/auth/success?token={jwt_token}"
    )
