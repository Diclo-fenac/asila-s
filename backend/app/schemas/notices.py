from datetime import datetime

from pydantic import BaseModel


class NoticeCreate(BaseModel):
    title: str
    content: str
    source_type: str
    location: str | None = None
    validity_start: datetime | None = None
    validity_end: datetime | None = None
    file_type: str


class NoticePreviewRequest(BaseModel):
    query: str
    location: str | None = None


class NoticePreviewChunk(BaseModel):
    chunk_text: str
    relevance_score: float


class NoticePreviewResponse(BaseModel):
    response: str
    retrieved_chunks: list[NoticePreviewChunk]


class NoticePublishResponse(BaseModel):
    status: str
    notice_id: str
