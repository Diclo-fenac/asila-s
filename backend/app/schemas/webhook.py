from pydantic import BaseModel


class WhatsAppWebhookRequest(BaseModel):
    From: str
    Body: str
    Latitude: str | None = None
    Longitude: str | None = None
    ProfileName: str | None = None


class WhatsAppWebhookResponse(BaseModel):
    status: str
    message: str
