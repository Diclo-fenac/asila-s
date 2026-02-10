from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_session
from app.db.tenancy import set_current_tenant


async def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.replace("Bearer ", "", 1)
    return decode_access_token(token)


def get_tenant_id(x_tenant_id: str | None = Header(default=None)) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-Tenant-Id")
    return x_tenant_id


async def get_tenant_session(
    tenant_id: str = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_session),
) -> AsyncSession:
    await set_current_tenant(session, tenant_id)
    return session
