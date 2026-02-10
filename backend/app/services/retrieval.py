from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class RetrievedChunk:
    chunk_text: str
    distance: float
    title: str | None
    location: str | None
    tenant_name: str | None


RAG_SQL = """
SELECT
    e.chunk_text,
    e.embedding <=> :query_embedding AS distance,
    n.title,
    n.location,
    t.name AS tenant_name
FROM embeddings e
JOIN notices n ON e.notice_id = n.id
JOIN tenants t ON e.tenant_id = t.id
WHERE
    n.publish_status = 'approved'
    AND (n.validity_end IS NULL OR n.validity_end > NOW())
    AND e.tenant_id = :tenant_id
    AND (:location IS NULL OR e.location = :location)
    AND t.is_active = TRUE
ORDER BY e.embedding <=> :query_embedding
LIMIT 5;
"""


async def retrieve_chunks(
    session: AsyncSession,
    tenant_id: str,
    query_embedding: list[float],
    location: str | None,
) -> list[RetrievedChunk]:
    result = await session.execute(
        text(RAG_SQL),
        {"tenant_id": tenant_id, "location": location, "query_embedding": query_embedding},
    )
    return [
        RetrievedChunk(
            chunk_text=row.chunk_text,
            distance=row.distance,
            title=row.title,
            location=row.location,
            tenant_name=row.tenant_name,
        )
        for row in result.mappings()
    ]
