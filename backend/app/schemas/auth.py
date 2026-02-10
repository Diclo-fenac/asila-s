from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    tenant_id: str
    tenant_name: str
    role: str
