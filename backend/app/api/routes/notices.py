from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_tenant_id
from app.db.session import get_session
from app.models import Notice
from app.schemas.notices import (
    NoticeCreate,
    NoticePreviewRequest,
    NoticePreviewResponse,
    NoticePublishResponse,
)
from app.services.ingestion import process_notice_upload
from app.services.rag import preview_notice_response

router = APIRouter()


@router.post("/notices")
async def create_notice(
    payload: NoticeCreate,
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    # Create draft notice (ingestion happens on publish)
    return {"status": "draft", "notice_id": "stub-id", "tenant_id": tenant_id}


@router.post("/notices/{notice_id}/preview", response_model=NoticePreviewResponse)
async def preview_notice(
    notice_id: str,
    payload: NoticePreviewRequest,
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
) -> NoticePreviewResponse:
    _ = tenant_id
    return preview_notice_response(payload.query, payload.location)


@router.post("/notices/{notice_id}/publish", response_model=NoticePublishResponse)
async def publish_notice(
    notice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
) -> NoticePublishResponse:
    _ = tenant_id
    return NoticePublishResponse(status="approved", notice_id=notice_id)
