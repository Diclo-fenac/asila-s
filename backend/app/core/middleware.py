from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_user
from app.services.ratelimit import check_admin_rate_limit


async def admin_rate_limit_middleware(user: dict = Depends(get_current_user)) -> dict:
    """Middleware to enforce admin API rate limits."""
    user_id = user.get("sub", "unknown")
    if not await check_admin_rate_limit(user_id, limit=100, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later."
        )
    return user
