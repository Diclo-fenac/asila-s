from pydantic import BaseModel


class BroadcastCreate(BaseModel):
    notice_id: str
    message: str
    target_location: str | None = None


class BroadcastResponse(BaseModel):
    id: str
    status: str
    sent_count: int
    failed_count: int
