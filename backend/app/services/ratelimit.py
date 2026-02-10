from __future__ import annotations

from functools import wraps

from fastapi import HTTPException, Request, status
from redis import asyncio as redis

from app.core.config import settings


async def check_rate_limit(phone: str, limit: int = 10, window_seconds: int = 3600) -> bool:
    """Check if phone number is within rate limit. Returns True if allowed."""
    client = redis.from_url(settings.redis_url, decode_responses=True)
    key = f"ratelimit:{phone}"
    
    try:
        current = await client.get(key)
        if current and int(current) >= limit:
            return False
        
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        await pipe.execute()
        return True
    except Exception:
        return True  # Fail open if Redis unavailable


async def check_admin_rate_limit(user_id: str, limit: int = 100, window_seconds: int = 60) -> bool:
    """Check admin API rate limit. Returns True if allowed."""
    client = redis.from_url(settings.redis_url, decode_responses=True)
    key = f"admin_ratelimit:{user_id}"
    
    try:
        current = await client.get(key)
        if current and int(current) >= limit:
            return False
        
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window_seconds)
        await pipe.execute()
        return True
    except Exception:
        return True
