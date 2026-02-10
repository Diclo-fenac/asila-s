from pydantic import BaseModel


class QueryAnalyticsResponse(BaseModel):
    total_queries: int
    answered_queries: int
    unanswered_queries: int
    automated_rate: float
    top_queries: list[dict]
    language_distribution: dict


class UnansweredQueriesResponse(BaseModel):
    week: str
    unanswered_queries: list[dict]


class BroadcastCoverageResponse(BaseModel):
    tenant_id: str
    coverage: list[dict]
