import os
import requests
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# 1️⃣ Redirect user to GitHub
@router.get("/github")
def github_login():
    github_auth_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={os.getenv('GITHUB_CLIENT_ID')}"
        "&scope=user"
    )
    return RedirectResponse(github_auth_url)


# 2️⃣ GitHub callback
@router.get("/github/callback")
def github_callback(request: Request):
    code = request.query_params.get("code")

    # Exchange code for access token
    token_response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": os.getenv("GITHUB_CLIENT_ID"),
            "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
            "code": code,
        },
    )

    access_token = token_response.json().get("access_token")

    # Fetch GitHub user
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    github_user = user_response.json()

    # Create JWT
    jwt_token = create_access_token(
        {
            "github_id": github_user["id"],
            "username": github_user["login"],
            "avatar": github_user["avatar_url"],
        }
    )

    # Redirect to frontend
    return RedirectResponse(
        f"{os.getenv('FRONTEND_URL')}/auth/success?token={jwt_token}"
    )
