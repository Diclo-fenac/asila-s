from __future__ import annotations

import uuid

from app.models import Notice


def chunk_text(text: str, max_tokens: int = 500) -> list[str]:
    """Simple chunker: split by paragraphs, fallback to sentences if too large."""
    paragraphs = text.split("\n\n")
    chunks = []
    for para in paragraphs:
        if len(para.split()) <= max_tokens:
            chunks.append(para.strip())
        else:
            sentences = para.split(". ")
            current_chunk = ""
            for sentence in sentences:
                if len((current_chunk + sentence).split()) <= max_tokens:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            if current_chunk:
                chunks.append(current_chunk.strip())
    return [c for c in chunks if c]


async def process_notice_upload(
    notice: Notice,
    file_content: bytes | None = None,
) -> list[dict]:
    """
    Stub ingestion pipeline:
    1. OCR if image (jpg/png)
    2. Chunk text
    3. Generate embeddings
    4. Return embedding data for DB insert
    """
    text = notice.content
    
    # OCR stub for images
    if notice.file_type in {"jpg", "png"} and file_content:
        # TODO: call cloud OCR service
        text = f"[OCR extracted from {notice.file_type}] {text}"
    
    chunks = chunk_text(text)
    embeddings_data = []
    
    for idx, chunk in enumerate(chunks):
        # TODO: call generate_embedding from llm service
        embedding = [0.01] * 1536  # stub
        embeddings_data.append({
            "id": uuid.uuid4(),
            "notice_id": notice.id,
            "tenant_id": notice.tenant_id,
            "chunk_text": chunk,
            "chunk_index": idx,
            "location": notice.location,
            "embedding": embedding,
        })
    
    return embeddings_data
