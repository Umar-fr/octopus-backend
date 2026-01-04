import os
from cryptography.fernet import Fernet

_key = os.getenv("GITHUB_TOKEN_SECRET")
if not _key:
    raise RuntimeError("GITHUB_TOKEN_SECRET not set")

fernet = Fernet(_key.encode())


def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
