from jose import jwt
from datetime import datetime, timedelta
import os

ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes: int = 60 * 24 * 7):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        os.getenv("JWT_SECRET"),
        algorithm=ALGORITHM
    )
