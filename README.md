# Asila - WhatsApp Public Information System

> Multi-tenant government/business communication platform: broadcasts via WhatsApp Channels + 1:1 RAG-powered bot

## Quick Start (Local Development)

### 1. Start infrastructure
```bash
docker-compose up -d postgres redis
```

### 2. Run backend
```bash
cd backend
cp .env.example .env
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --port 8000
```

### 3. Test
```bash
poetry run pytest
```

## Architecture Overview

```
WhatsApp (Twilio) → FastAPI Webhooks → RAG Pipeline → PostgreSQL+pgvector
                                      ↓
                                  Redis Cache
```

**Key features:**
- Multi-tenant isolation (row-level security)
- Redis-based response caching (~24h TTL)
- Rate limiting (10 msg/hr per phone)
- Multi-language auto-detection
- Forbidden keyword filtering
- OCR for image-based notices
- Broadcast targeting by location/interaction history

## Project Structure

```
backend/
  app/
    api/routes/      # HTTP endpoints
    core/            # Auth, deps, config
    db/              # SQLAlchemy session + tenancy
    models/          # DB models
    schemas/         # Pydantic schemas
    services/        # Business logic
  alembic/           # DB migrations
  tests/             # Pytest suite
  
design.md            # Full architecture doc
requirements.md      # Functional requirements
slides.md            # Pitch deck content
dashboard-wireframe/ # UI mockups
work-done.md         # Progress log
```

## API Endpoints

### Webhooks (no auth)
- `POST /webhook/whatsapp` - Receive messages from Twilio
- `POST /webhook/status` - Delivery callbacks

### Admin (JWT + X-Tenant-Id required)
- `POST /api/auth/login` - Get token
- `POST /api/notices` - Upload notice
- `POST /api/notices/{id}/preview` - Test query simulation
- `POST /api/notices/{id}/publish` - Trigger ingestion
- `POST /api/broadcasts` - Send broadcast
- `GET /api/analytics/*` - Query stats, coverage, unanswered

## Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/asila
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key
ENV=local|production
```

## TODOs for Production

1. **LLM Integration** - Replace stubs in `backend/app/services/llm.py` with Bedrock/OpenAI
2. **Twilio Setup** - Add credentials for WhatsApp broadcast sending
3. **OCR Service** - Wire cloud OCR in `backend/app/services/ingestion.py`
4. **DB Retrieval** - Uncomment pgvector query in `backend/app/services/query.py`
5. **Monitoring** - Add CloudWatch/logging

## Documentation

- **[design.md](design.md)** - Complete system architecture, DB schema, API specs, RAG pipeline
- **[requirements.md](requirements.md)** - Functional/non-functional requirements, workflows
- **[slides.md](slides.md)** - USP, competitive analysis, AWS architecture
- **[backend/DEPLOYMENT.md](backend/DEPLOYMENT.md)** - Deployment guide
- **[work-done.md](work-done.md)** - Development progress log

## Testing

```bash
cd backend
poetry run pytest -v
```

Current coverage: webhook routes, cache helpers, rate limiting (all passing).

## Docker Deployment

```bash
# Full stack
docker-compose up -d

# Backend only
cd backend
docker build -t asila-backend .
docker run -p 8000:8000 --env-file .env asila-backend
```

## License

See project documentation for licensing details.

## Contact

Built for AI for Bharat Hackathon 2026.
