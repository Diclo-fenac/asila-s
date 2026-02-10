from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_tenant_id
from app.db.session import get_session
from app.schemas.broadcasts import BroadcastCreate, BroadcastResponse
from app.services.broadcast import get_broadcast_targets, send_whatsapp_broadcast

router = APIRouter()


@router.post("/broadcasts", response_model=BroadcastResponse)
async def create_broadcast(
    payload: BroadcastCreate,
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> BroadcastResponse:
    targets = await get_broadcast_targets(session, tenant_id, payload.target_location)
    sent, failed = await send_whatsapp_broadcast(targets, payload.message)
    return BroadcastResponse(id="stub-id", status="sent", sent_count=sent, failed_count=failed)
