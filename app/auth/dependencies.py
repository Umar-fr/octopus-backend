from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.utils.jwt import decode_access_token
from app.utils.db import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/github")


def get_current_user(token: str = Depends(oauth2_scheme)):
    
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()
    try:
        user = db.query(User).filter(
            User.github_id == payload["github_id"]
        ).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    
    finally:
        db.close()
