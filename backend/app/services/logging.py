from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Query, UnansweredQuery


async def log_query(
    session: AsyncSession,
    phone_number: str,
    tenant_id: str | None,
    query_text: str,
    query_language: str,
    location: str | None,
    response_text: str | None,
    response_language: str | None,
    response_type: str,
    retrieved_chunks: list[uuid.UUID] | None,
    latency_ms: int | None,
) -> None:
    query = Query(
        id=uuid.uuid4(),
        phone_number=phone_number,
        tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
        query_text=query_text,
        query_language=query_language,
        location=location,
        response_text=response_text,
        response_language=response_language,
        response_type=response_type,
        retrieved_chunks=retrieved_chunks,
        latency_ms=latency_ms,
    )
    session.add(query)
    await session.commit()


async def log_unanswered_query(
    session: AsyncSession,
    phone_number: str,
    tenant_id: str | None,
    query_text: str,
    query_language: str,
    location: str | None,
    reason: str,
) -> None:
    unanswered = UnansweredQuery(
        id=uuid.uuid4(),
        phone_number=phone_number,
        tenant_id=uuid.UUID(tenant_id) if tenant_id else None,
        query_text=query_text,
        query_language=query_language,
        location=location,
        reason=reason,
    )
    session.add(unanswered)
    await session.commit()
