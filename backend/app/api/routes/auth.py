from fastapi import APIRouter

from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth import authenticate_user

router = APIRouter()


@router.post("/auth/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
    return authenticate_user(payload.username, payload.password)
