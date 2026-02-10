from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def set_current_tenant(session: AsyncSession, tenant_id: str) -> None:
    await session.execute(text("SET LOCAL app.current_tenant_id = :tenant_id"), {"tenant_id": tenant_id})
