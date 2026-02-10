from __future__ import annotations

import hashlib
import uuid

from sqlalchemy import insert

from app.models import Query, UnansweredQuery
from app.schemas.webhook import WhatsAppWebhookRequest, WhatsAppWebhookResponse
from app.services.cache import (
    build_cache_key,
    get_cached_response,
    get_redis_client,
    set_cached_response,
)
from app.services.intent import classify_intent
from app.services.llm import detect_language, generate_embedding, generate_response


def build_intent_hash(message: str, department: str | None) -> str:
    digest = hashlib.sha256()
    digest.update(message.lower().encode("utf-8"))
    if department:
        digest.update(department.encode("utf-8"))
    return digest.hexdigest()[:12]


async def handle_whatsapp_message(payload: WhatsAppWebhookRequest) -> WhatsAppWebhookResponse:
    from app.services.guardrails import post_process_response
    from app.services.ratelimit import check_rate_limit
    
    phone = payload.From.replace("whatsapp:", "")
    message = payload.Body
    
    # Rate limit check
    if not await check_rate_limit(phone, limit=10, window_seconds=3600):
        return WhatsAppWebhookResponse(
            status="rate_limited",
            message="You have reached the hourly message limit. Please try again later."
        )
    location = None  # TODO: extract from payload or session
    intent = classify_intent(message)
    language = detect_language(message)
    intent_hash = build_intent_hash(message, intent.department)
    
    from app.services.tenants import map_department_to_tenant
    tenant_id = map_department_to_tenant(intent.department)
    cache_key = build_cache_key(tenant_id, location, intent_hash, language)
    
    client = get_redis_client()
    try:
        cached = await get_cached_response(client, cache_key)
        if cached:
            return WhatsAppWebhookResponse(status="cached", message=cached)
    except Exception:
        pass  # Redis not available
    
    # Generate embedding and retrieve chunks (stub for now - no DB dependency)
    embedding = await generate_embedding(message)
    _ = embedding
    
    # TODO: wire retrieval when DB is ready
    # async with AsyncSessionLocal() as session:
    #     chunks = await retrieve_chunks(session, tenant_id, embedding, location)
    #     context_texts = [c.chunk_text for c in chunks]
    context_texts = []
    
    # Generate response
    if not context_texts:
        response_text = "No verified information available"
        response_type = "fallback"
    else:
        raw_response = await generate_response(context_texts, message)
        response_text, is_safe = post_process_response(raw_response)
        response_type = "rag" if is_safe else "filtered"
    
    try:
        await set_cached_response(client, cache_key, response_text)
    except Exception:
        pass  # Redis not available
    
    # TODO: log query to DB with session
    _ = phone
    _ = language
    _ = response_type
    
    return WhatsAppWebhookResponse(status=response_type, message=response_text)
