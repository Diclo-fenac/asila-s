# Asila Backend - Deployment Guide

## Prerequisites
- Python 3.11+
- PostgreSQL 15+ with pgvector extension
- Redis 6+
- Poetry or pip

## Local Setup

### 1. Install dependencies
```bash
cd backend
poetry install
# or
pip install -r requirements.txt
```

### 2. Environment variables
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

Edit `.env`:
```
ENV=local
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/asila
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key
```

### 3. Database setup
```bash
# Install pgvector extension in PostgreSQL
psql -U postgres -d asila -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run migrations
poetry run alembic revision --autogenerate -m "init"
poetry run alembic upgrade head
```

### 4. Run server
```bash
poetry run uvicorn app.main:app --reload --port 8000
```

### 5. Run tests
```bash
poetry run pytest
```

## Production Deployment

### Docker
```bash
docker build -t asila-backend .
docker run -p 8000:8000 --env-file .env asila-backend
```

### Environment-specific settings
- Set `ENV=production` in production
- Use managed PostgreSQL with pgvector
- Use managed Redis (ElastiCache, etc.)
- Configure proper JWT secret rotation
- Set up SSL/TLS termination at load balancer

## API Endpoints

### Webhooks (no auth)
- `POST /webhook/whatsapp` - Twilio webhook
- `POST /webhook/status` - Delivery status

### Admin API (requires JWT + X-Tenant-Id)
- `POST /api/auth/login` - Get JWT token
- `POST /api/notices` - Create notice
- `POST /api/notices/{id}/preview` - Preview response
- `POST /api/notices/{id}/publish` - Publish notice
- `POST /api/broadcasts` - Trigger broadcast
- `GET /api/analytics/queries` - Query analytics
- `GET /api/analytics/unanswered` - Unanswered queries
- `GET /api/analytics/broadcast-coverage` - Coverage map

## Next Steps
1. Connect cloud LLM provider (Bedrock/OpenAI) in `app/services/llm.py`
2. Add Twilio WhatsApp credentials for broadcast sending
3. Uncomment DB retrieval in `app/services/query.py` after DB initialization
4. Configure OCR service in `app/services/ingestion.py`
5. Set up monitoring/logging (CloudWatch, etc.)
