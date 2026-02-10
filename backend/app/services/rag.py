from app.schemas.notices import NoticePreviewResponse


def preview_notice_response(query: str, location: str | None = None) -> NoticePreviewResponse:
    return NoticePreviewResponse(
        response="Preview response placeholder.",
        retrieved_chunks=[{"chunk_text": "Sample chunk text", "relevance_score": 0.92}],
    )
