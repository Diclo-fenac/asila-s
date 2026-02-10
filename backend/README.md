# Asila Backend

FastAPI backend for the Asila WhatsApp public information system.

## What’s inside
- FastAPI app with webhook + admin routes.
- Async SQLAlchemy scaffolding for PostgreSQL + pgvector.
- Redis cache client wiring (response cache + rate limits).
- Stubbed endpoints ready for implementation.

## Quickstart (Poetry)
1. Install dependencies.
2. Configure environment variables.
3. Run the API server.

Environment variables (see `.env.example`):
- `DATABASE_URL` (PostgreSQL async URL)
- `REDIS_URL`
- `JWT_SECRET`
- `ENV`

## Notes
- Webhook routes are under `/webhook/*`.
- Admin routes are under `/api/*`.
- Admin routes require `Authorization: Bearer <token>` and `X-Tenant-Id` headers.
- Only approved + unexpired notices should be retrievable (see `design.md`).
- Cache key pattern: `cache:{tenant_id}:{location}:{intent_hash}:{language}`.
