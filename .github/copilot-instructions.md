# Copilot Instructions for Asila

## Big picture
- WhatsApp-first public info system for multi-tenant government/business teams: broadcasts via Channels + 1:1 bot via Twilio WhatsApp (see `design.md`, `requirements.md`, `slides.md`).
- Backend: FastAPI + async (httpx), PostgreSQL 15 + pgvector, Redis (mandatory), SQLAlchemy 2 + Alembic; LLM/embeddings via cloud provider (Bedrock in slides). Frontend: React 18 (MUI/Tailwind possible) for admin dashboard.
- Hard requirements: strict tenant isolation everywhere, verified sources only, multi-language responses mirror the user’s language, optimized for WhatsApp cost (cache responses aggressively).

## Domain & data
- Core tables (see `design.md §2`): `tenants`, `notices`, `embeddings`, `users`, `queries`, `unanswered_queries`, `broadcasts`; row-level security enforced per `tenant_id`.
- Notices: status enum `draft/approved/archived`; only approved + unexpired content is retrievable/indexed. Images (jpg/png) go through OCR; store original path, embed extracted text.
- Embeddings: 1536-dim vectors; chunk text ≈500 tokens; keep `chunk_index`, `location`, `tenant_id` for filtering.
- Redis keys: session/context + rate limits; response cache pattern `cache:{tenant_id}:{location}:{intent_hash}:{language}` with ~24h TTL and manual invalidation on notice updates.

## Workflows to preserve
- Document ingestion: upload → store original (S3-like) → OCR if image → validate as draft → preview/simulate → approve → chunk → embed → write to pgvector with tenant/location metadata → ready for retrieval.
- Query handling: Twilio webhook extracts phone, message, location; check Redis session & cache → classify via keywords (dept/location) → vector search filtered by tenant, location, validity, status → top 3–5 chunks → LLM with strict system prompt → post-check forbidden keywords → cache + log query.
- Broadcasts: manual trigger only (uploads do NOT auto-send); target users who interacted + opted-in, optionally by location; log sent/failed and update coverage metrics.

## Behavioral guardrails
- Respond "No verified information available" (or provide tenant contact) when retrieval fails or intent unclear after one clarifying question; log to `unanswered_queries`.
- No diagnosis/speculation/impersonation; post-process for forbidden keywords before sending.
- Rate limits: ~10 messages/hour per phone; admin API ~100 req/min; keep tenant-scoped limits in Redis.
- Multi-language: auto-detect via LLM; reply in the same language; store `query_language`/`response_language` for analytics.

## API & frontend patterns
- Webhooks: `POST /webhook/whatsapp` (TwiML/JSON ack) and `/webhook/status` for delivery callbacks.
- Admin APIs: JWT auth; endpoints for notices (upload, preview, publish), broadcasts, analytics (queries/unanswered/broadcast coverage). Enforce tenant scoping server-side, never trust client.
- Dashboard UX cues (see `dashboard-wireframe/*`): upload/approve flow, notice preview with retrieved chunks, broadcast coverage map, unanswered queries feedback loop.

## Engineering conventions
- Prefer async FastAPI routes; use SQLAlchemy 2 with parameterized queries; apply RLS + `current_setting('app.current_tenant_id')` when querying.
- Tests: pytest for backend flows (ingestion, retrieval filters, cache hit/miss) and Jest for frontend; include sample fixtures per tenant/location.
- Caching first: check cache before LLM; invalidate on notice change; avoid duplicate embeddings.
- Assume cloud-agnostic deployment via Docker/Fargate; object storage is S3-compatible.

## Sources of truth
- Detailed architecture, DB schema, and prompts: `design.md`.
- Functional/non-functional requirements and guardrails: `requirements.md`.
- Narrative, USP, and AWS-oriented architecture: `slides.md`.
- UI references: `dashboard-wireframe/` images.
