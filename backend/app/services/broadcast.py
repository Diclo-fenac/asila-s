from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Broadcast, User


async def get_broadcast_targets(
    session: AsyncSession,
    tenant_id: str,
    location: str | None = None,
) -> list[str]:
    """Get phone numbers for broadcast targeting."""
    # TODO: query users who interacted + opted-in + match location
    return []


async def send_whatsapp_broadcast(phone_numbers: list[str], message: str) -> tuple[int, int]:
    """Stub for sending broadcast via Twilio/WhatsApp Channels."""
    sent = len(phone_numbers)
    failed = 0
    # TODO: integrate Twilio API
    return sent, failed
