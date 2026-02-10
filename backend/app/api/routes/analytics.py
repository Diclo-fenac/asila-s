from fastapi import APIRouter, Depends

from app.core.deps import get_current_user, get_tenant_id
from app.schemas.analytics import BroadcastCoverageResponse, QueryAnalyticsResponse, UnansweredQueriesResponse

router = APIRouter()


@router.get("/analytics/queries", response_model=QueryAnalyticsResponse)
async def query_analytics(
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
) -> QueryAnalyticsResponse:
    _ = tenant_id
    return QueryAnalyticsResponse(
        total_queries=150,
        answered_queries=120,
        unanswered_queries=30,
        automated_rate=0.7,
        top_queries=[
            {"query": "vaccination camp", "count": 45, "language": "hi"},
            {"query": "power outage", "count": 30, "language": "en"},
        ],
        language_distribution={"hi": 60, "en": 50, "ta": 40},
    )


@router.get("/analytics/unanswered", response_model=UnansweredQueriesResponse)
async def unanswered_analytics(
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
) -> UnansweredQueriesResponse:
    _ = tenant_id
    return UnansweredQueriesResponse(
        week="2026-01-19 to 2026-01-25",
        unanswered_queries=[
            {
                "query": "garbage collection schedule",
                "count": 37,
                "locations": ["Ward 5", "Ward 12"],
                "languages": ["hi", "en"],
            }
        ],
    )


@router.get("/analytics/broadcast-coverage", response_model=BroadcastCoverageResponse)
async def broadcast_coverage(
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user),
) -> BroadcastCoverageResponse:
    return BroadcastCoverageResponse(
        tenant_id=tenant_id,
        coverage=[
            {
                "location": "Ward 12",
                "boundary": {"type": "Polygon", "coordinates": []},
                "sent_count": 150,
                "success_rate": 0.95,
            }
        ],
    )
