from app.core.security import create_access_token
from app.schemas.auth import LoginResponse


def authenticate_user(username: str, password: str) -> LoginResponse:
    token = create_access_token(subject=username)
    return LoginResponse(
        token=token,
        tenant_id="00000000-0000-0000-0000-000000000000",
        tenant_name="Demo Tenant",
        role="admin",
    )
