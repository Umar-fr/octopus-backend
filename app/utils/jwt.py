from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

ALGORITHM = "HS256"
JWT_SECRET = os.getenv("JWT_SECRET")


def create_access_token(data: dict, expires_minutes: int = 60 * 24 * 7):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        JWT_SECRET,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None
