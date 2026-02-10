# Work Done Log

## 2026-01-29
### Backend scaffold (FastAPI)
- Added `backend/` service with FastAPI app and routes: webhooks, notices, broadcasts, analytics.
- Added async SQLAlchemy session scaffolding and tenant RLS helper.
- Added Redis cache helpers and intent classification stubs.
- Added pgvector retrieval SQL skeleton (see `backend/app/services/retrieval.py`).
- Added JWT utilities + dependencies (minimal; not expanding further per latest guidance).
- Added tests for health check, webhook (JSON + form), cache key helper.
- **Added LLM service stubs** (embedding generation, response generation, language detection).
- **Added query logging helpers** for `queries` and `unanswered_queries` tables.
- **Added ingestion pipeline stubs** (chunking, OCR placeholder, embedding generation).
- **Wired webhook handler** to use embedding stub + cache path + response generation.
- **Added guardrails** (forbidden keyword post-processing).
- **Added broadcast service** (user targeting + Twilio send stub).
- **Set up Alembic** for DB migrations (env.py configured, models imported).
- **Added rate limiting** (10 msg/hour per phone, 100 req/min for admin APIs).
- **Added user context management** (session memory, location tracking).
- **Added department-to-tenant mapping** (keyword-based routing).

### Files & key paths
- `backend/app/main.py` entrypoint
- `backend/app/api/routes/*` HTTP routes (webhook, auth, notices, broadcasts, analytics)
- `backend/app/services/intent.py` keyword-based intent classifier
- `backend/app/services/cache.py` Redis helpers + cache key builder
- `backend/app/services/query.py` webhook handler with full flow (rate limit, cache, embedding, retrieval, guardrails)
- `backend/app/services/llm.py` LLM stubs (embedding, response generation, language detection)
- `backend/app/services/logging.py` query logging helpers
- `backend/app/services/ingestion.py` chunking + OCR + embedding pipeline stubs
- `backend/app/services/retrieval.py` pgvector SQL retrieval function
- `backend/app/services/guardrails.py` forbidden keyword post-processing
- `backend/app/services/broadcast.py` user targeting + Twilio send stub
- `backend/app/services/ratelimit.py` Redis-based rate limiting (phone + admin)
- `backend/app/services/users.py` user context management (location, language, session TTL)
- `backend/app/services/tenants.py` department-to-tenant mapping
- `backend/app/core/middleware.py` admin rate limit middleware
- `backend/app/models/*` SQLAlchemy models aligned to `design.md`
- `backend/alembic/` migrations directory (configured)
- `backend/tests/test_app.py` smoke tests

### Known TODOs / Next steps (fast-path)
- Connect real cloud LLM provider (Bedrock/OpenAI) for embeddings + response generation.
- Uncomment DB retrieval call in query handler when Postgres + pgvector ready.
- Add DB session to webhook handler for query logging (once DB initialized).
- Wire ingestion pipeline to notices publish endpoint + save embeddings to DB.
- Run Alembic migration to create DB schema (`alembic revision --autogenerate -m "init"`, `alembic upgrade head`).
- Add rate limiting middleware (Redis counters per phone).
- Add user session management (remember location for 5-10 min).
- Add department-to-tenant mapping logic.
- Add Twilio WhatsApp API integration for broadcast sending.
