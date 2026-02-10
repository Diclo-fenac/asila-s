from fastapi import APIRouter, Request

from app.schemas.webhook import WhatsAppWebhookRequest, WhatsAppWebhookResponse
from app.services.query import handle_whatsapp_message

router = APIRouter()


@router.post("/webhook/whatsapp", response_model=WhatsAppWebhookResponse)
async def whatsapp_webhook(request: Request) -> WhatsAppWebhookResponse:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        raw_payload = await request.json()
    else:
        form = await request.form()
        raw_payload = dict(form)
    payload = WhatsAppWebhookRequest(**raw_payload)
    return await handle_whatsapp_message(payload)


@router.post("/webhook/status")
async def whatsapp_status_callback() -> dict:
    return {"status": "ok"}
