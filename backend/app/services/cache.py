import hashlib

from redis import asyncio as redis

from app.core.config import settings


def get_redis_client() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


def build_cache_key(tenant_id: str, location: str | None, intent_hash: str, language: str) -> str:
    location_key = (location or "all").lower().replace(" ", "-")
    return f"cache:{tenant_id}:{location_key}:{intent_hash}:{language}"


def hash_intent(seed: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8"))
    return digest.hexdigest()[:12]


async def get_cached_response(client: redis.Redis, cache_key: str) -> str | None:
    return await client.get(cache_key)


async def set_cached_response(client: redis.Redis, cache_key: str, value: str, ttl_seconds: int = 86400) -> None:
    await client.set(cache_key, value, ex=ttl_seconds)
