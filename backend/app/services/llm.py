from __future__ import annotations


async def generate_embedding(text: str) -> list[float]:
    """Stub for cloud LLM embedding generation. Returns mock 1536-dim vector."""
    return [0.01] * 1536


async def generate_response(context_chunks: list[str], query: str) -> str:
    """Stub for cloud LLM response generation using retrieved context."""
    if not context_chunks:
        return "No verified information available"
    return f"Based on official sources: {context_chunks[0][:100]}..."


def detect_language(text: str) -> str:
    """Stub language detection. Returns 'en' by default."""
    return "en"
