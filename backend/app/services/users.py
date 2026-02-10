from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_or_create_user(session: AsyncSession, phone_number: str) -> User:
    """Get existing user or create new one."""
    result = await session.execute(select(User).where(User.phone_number == phone_number))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            phone_number=phone_number,
            last_interaction_at=datetime.utcnow(),
            opted_out=False,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        user.last_interaction_at = datetime.utcnow()
        await session.commit()
    
    return user


async def get_user_context(session: AsyncSession, phone_number: str, ttl_minutes: int = 5) -> dict | None:
    """Get user's recent context (location, last query) if within TTL."""
    result = await session.execute(select(User).where(User.phone_number == phone_number))
    user = result.scalar_one_or_none()
    
    if not user or not user.last_interaction_at:
        return None
    
    if datetime.utcnow() - user.last_interaction_at > timedelta(minutes=ttl_minutes):
        return None
    
    return {
        "location": user.last_known_location,
        "language": user.preferred_language,
    }


async def update_user_context(
    session: AsyncSession,
    phone_number: str,
    location: str | None = None,
    language: str | None = None,
) -> None:
    """Update user's context (location, language)."""
    result = await session.execute(select(User).where(User.phone_number == phone_number))
    user = result.scalar_one_or_none()
    
    if user:
        if location:
            user.last_known_location = location
        if language:
            user.preferred_language = language
        await session.commit()
