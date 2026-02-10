import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.cache import build_cache_key


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_webhook_whatsapp():
    payload = {"From": "whatsapp:+123", "Body": "hello"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/webhook/whatsapp", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] in {"fallback", "cached", "generated", "rag", "filtered", "rate_limited"}


@pytest.mark.asyncio
async def test_webhook_whatsapp_form():
    payload = {"From": "whatsapp:+123", "Body": "power outage"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/webhook/whatsapp", data=payload)
    assert response.status_code == 200
    assert response.json()["status"] in {"fallback", "cached", "generated", "rag", "filtered", "rate_limited"}


def test_cache_key_builder():
    cache_key = build_cache_key("tenant-1", "Ward 12", "abc123", "hi")
    assert cache_key == "cache:tenant-1:ward-12:abc123:hi"
