from datetime import datetime, timedelta

from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.core.config import settings


class TokenError(HTTPException):
    def __init__(self, detail: str = "Invalid token") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenError() from exc
