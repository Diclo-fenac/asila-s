# Design Document: 'Asila - WhatsApp-Based Public Information System

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────┐
│   Citizens  │
└──────┬──────┘
       │ WhatsApp (Multi-language)
       ▼
┌─────────────────────────────────────────────────────────┐
│                    WhatsApp Layer                        │
│  ┌──────────────┐         ┌──────────────────────────┐ │
│  │   Channels   │         │  1-to-1 Bot (Twilio)     │ │
│  │  (Broadcast) │         │  (Query/Response)        │ │
│  └──────────────┘         └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
       │                              │
       │                              ▼
       │                    ┌──────────────────┐
       │                    │  Webhook Service │
       │                    │  (FastAPI)       │
       │                    └──────────────────┘
       │                              │
       │                              ▼
       │                    ┌──────────────────┐
       │                    │  Query Processor │
       │                    │  - Classify      │
       │                    │  - Extract       │
       │                    │  - Route         │
       │                    │  - Tenant Check  │
       │                    └──────────────────┘
       │                              │
       │                              ▼
       │                    ┌──────────────────┐
       │                    │   RAG Pipeline   │
       │                    │  - Retrieve      │
       │                    │  - Generate      │
       │                    │  - Cache (Redis) │
       │                    └──────────────────┘
       │                              │
       │                              ▼
       │                    ┌──────────────────┐
       │                    │  LLM Service     │
       │                    │  (Cloud-based)   │
       │                    │  Multi-language  │
       │                    └──────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│         Admin Dashboard (React) - Multi-Tenant          │
│  - Upload Documents (PDF/JPG with OCR)                  │
│  - Preview/Simulate                                      │
│  - Trigger Broadcasts                                    │
│  - View Analytics                                        │
│  - Map-based Broadcast Coverage                          │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│           Data Ingestion Pipeline                        │
│  - Parse Documents (PDF/DOCX/Text)                       │
│  - OCR for Images (Cloud OCR Service)                    │
│  - Chunk Text                                            │
│  - Generate Embeddings (Cloud LLM)                       │
│  - Store in PostgreSQL + pgvector                        │
└─────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│         PostgreSQL + pgvector Database                   │
│  - Tenants (Departments/Businesses)                      │
│  - Notices (with tenant_id)                              │
│  - Embeddings (with tenant_id)                           │
│  - Users                                                 │
│  - Analytics (tenant-isolated)                           │
│                                                          │
│         Redis Cache (Mandatory)                          │
│  - Response cache                                        │
│  - Session storage                                       │
│  - Rate limiting                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Component Breakdown

**Component 1: WhatsApp Layer**
- WhatsApp Channels for one-way broadcasts
- Twilio WhatsApp Business API for 1-to-1 queries
- Multi-language support (citizens query in any language)

**Component 2: Backend Service (FastAPI)**
- Webhook endpoint for incoming messages
- Query processor (classify, extract, route, tenant isolation)
- RAG pipeline (retrieve, generate, cache via Redis)
- Admin API endpoints (multi-tenant aware)
- Analytics aggregation (tenant-isolated)

**Component 3: Admin Dashboard (React)**
- Multi-tenant interface (each tenant sees only their data)
- Document upload interface (PDF/DOCX/JPG/PNG with OCR)
- Preview/simulation tool
- Broadcast trigger
- Analytics dashboard
- Map-based broadcast coverage (ward/area boundaries)

**Component 4: Data Ingestion Pipeline**
- Document parser (PDF, DOCX, text)
- Cloud OCR service for images (JPG, PNG)
- Text chunker (~500 tokens)
- Embedding generator (Cloud LLM)
- Database writer (with tenant_id)

**Component 5: PostgreSQL + pgvector**
- Single source of truth
- Vector similarity search
- Metadata filtering
- Multi-tenant data isolation

**Component 6: Redis Cache (Mandatory)**
- Response caching
- Session storage
- Rate limiting
- Performance optimization

**Component 7: Cloud LLM Service**
- Text embeddings (1536 dims)
- Response generation
- Multi-language input/output
- No separate translation service needed

**Component 8: Cloud OCR Service**
- Image to text extraction
- Supports JPG, PNG formats
- Runs during document upload

---

## 2. Database Schema

### 2.1 Core Tables

**tenants** (NEW - Multi-tenancy support)
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'government', 'business', 'corporate'
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    office_address TEXT,
    working_hours VARCHAR(100),
    allowed_source_types TEXT[], -- ['official_notice', 'advisory']
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CHECK (type IN ('government', 'business', 'corporate'))
);

CREATE INDEX idx_tenants_type ON tenants(type);
CREATE INDEX idx_tenants_active ON tenants(is_active);
```

**departments** (DEPRECATED - merged into tenants)
```sql
-- This table is replaced by 'tenants' table
-- Keeping for reference during migration
```

**notices**
```sql
CREATE TABLE notices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- official_notice, advisory, service_notice
    approved_by VARCHAR(100),
    publish_status VARCHAR(20) DEFAULT 'draft', -- draft, approved, archived
    location VARCHAR(100), -- ward, area, pincode
    validity_start TIMESTAMP,
    validity_end TIMESTAMP,
    file_type VARCHAR(20), -- pdf, docx, jpg, png, text
    original_file_path TEXT, -- object storage path
    ocr_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    archived_at TIMESTAMP,
    
    CHECK (source_type IN ('official_notice', 'advisory', 'service_notice')),
    CHECK (publish_status IN ('draft', 'approved', 'archived')),
    CHECK (file_type IN ('pdf', 'docx', 'jpg', 'png', 'text'))
);

CREATE INDEX idx_notices_tenant ON notices(tenant_id);
CREATE INDEX idx_notices_location ON notices(location);
CREATE INDEX idx_notices_status ON notices(publish_status);
CREATE INDEX idx_notices_validity ON notices(validity_start, validity_end);
CREATE INDEX idx_notices_ocr ON notices(ocr_processed);

-- Row-level security for tenant isolation
ALTER TABLE notices ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON notices
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

**embeddings**
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notice_id UUID REFERENCES notices(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(1536), -- Cloud LLM embedding dimension
    location VARCHAR(100), -- denormalized
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_embeddings_notice ON embeddings(notice_id);
CREATE INDEX idx_embeddings_tenant ON embeddings(tenant_id);
CREATE INDEX idx_embeddings_location ON embeddings(location);
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops);

-- Row-level security for tenant isolation
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON embeddings
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

**users**
```sql
CREATE TABLE users (
    phone_number VARCHAR(20) PRIMARY KEY,
    last_known_location VARCHAR(100),
    subscribed_tenants UUID[], -- array of tenant IDs
    last_interaction_at TIMESTAMP,
    opted_out BOOLEAN DEFAULT FALSE,
    preferred_language VARCHAR(10), -- detected from queries, optional
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_location ON users(last_known_location);
CREATE INDEX idx_users_last_interaction ON users(last_interaction_at);
CREATE INDEX idx_users_language ON users(preferred_language);
```

**location_aliases**
```sql
CREATE TABLE location_aliases (
    alias VARCHAR(100) PRIMARY KEY,
    canonical_location VARCHAR(100) NOT NULL
);

-- Example data:
-- INSERT INTO location_aliases VALUES ('Sector 5', 'Ward 12');
```

**queries**
```sql
CREATE TABLE queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) REFERENCES users(phone_number),
    tenant_id UUID REFERENCES tenants(id),
    query_text TEXT NOT NULL,
    query_language VARCHAR(10), -- detected language
    location VARCHAR(100),
    response_text TEXT,
    response_language VARCHAR(10),
    response_type VARCHAR(50), -- cached, rag, fallback, redirect
    retrieved_chunks UUID[], -- array of embedding IDs
    latency_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_queries_phone ON queries(phone_number);
CREATE INDEX idx_queries_tenant ON queries(tenant_id);
CREATE INDEX idx_queries_created ON queries(created_at);
CREATE INDEX idx_queries_language ON queries(query_language);

-- Row-level security for tenant isolation
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON queries
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

**unanswered_queries**
```sql
CREATE TABLE unanswered_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20),
    tenant_id UUID REFERENCES tenants(id),
    query_text TEXT NOT NULL,
    query_language VARCHAR(10),
    location VARCHAR(100),
    reason VARCHAR(100), -- no_data, out_of_scope, low_confidence
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_unanswered_tenant ON unanswered_queries(tenant_id);
CREATE INDEX idx_unanswered_created ON unanswered_queries(created_at);

-- Row-level security for tenant isolation
ALTER TABLE unanswered_queries ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON unanswered_queries
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

**broadcasts**
```sql
CREATE TABLE broadcasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    notice_id UUID REFERENCES notices(id),
    message_text TEXT NOT NULL,
    target_location VARCHAR(100),
    sent_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_broadcasts_tenant ON broadcasts(tenant_id);
CREATE INDEX idx_broadcasts_created ON broadcasts(created_at);

-- Row-level security for tenant isolation
ALTER TABLE broadcasts ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON broadcasts
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

**response_cache**
```sql
-- This is now handled by Redis, not PostgreSQL
-- Keeping for reference

-- Redis key structure:
-- cache:{tenant_id}:{location}:{intent_hash} -> response_json
-- Example: cache:uuid-123:ward-12:abc123 -> {"response": "...", "chunks": [...]}
```

---

## 3. API Design

### 3.1 Webhook Endpoints (FastAPI)

**POST /webhook/whatsapp**
- Receives incoming WhatsApp messages from Twilio
- Request body:
```json
{
  "From": "whatsapp:+919876543210",
  "Body": "vaccination camp near me",
  "Latitude": "12.9716",
  "Longitude": "77.5946"
}
```
- Response: TwiML or JSON acknowledgment
- Processing:
  1. Extract phone number, message, location
  2. Classify intent and department
  3. Retrieve from vector DB
  4. Generate response via Bedrock
  5. Send response via Twilio
  6. Log query

**POST /webhook/status**
- Receives delivery status callbacks from Twilio
- Logs delivery success/failure

---

### 3.2 Admin API Endpoints

**Authentication**
- Simple JWT-based auth
- Role: admin, department_user

**POST /api/auth/login**
```json
{
  "username": "health_admin",
  "password": "secure_password"
}
```
Response:
```json
{
  "token": "jwt_token",
  "tenant_id": "uuid",
  "tenant_name": "Health Department",
  "role": "admin"
}
```

**POST /api/notices**
- Upload new notice (tenant-scoped)
```json
{
  "title": "Vaccination Camp - Ward 12",
  "content": "Camp on Jan 30, 10 AM to 4 PM at Community Center",
  "source_type": "official_notice",
  "location": "Ward 12",
  "validity_start": "2026-01-30T10:00:00Z",
  "validity_end": "2026-01-30T16:00:00Z",
  "file_type": "jpg"
}
```
- If file_type is jpg/png, OCR is triggered automatically

**POST /api/notices/{id}/preview**
- Simulate query against notice
```json
{
  "query": "vaccination camp near me",
  "location": "Ward 12"
}
```
Response:
```json
{
  "response": "Vaccination camp in Ward 12 on Jan 30...",
  "retrieved_chunks": [
    {
      "chunk_text": "Camp on Jan 30...",
      "relevance_score": 0.92
    }
  ]
}
```

**POST /api/notices/{id}/publish**
- Mark notice as approved and trigger ingestion

**POST /api/broadcasts**
- Trigger broadcast
```json
{
  "notice_id": "uuid",
  "message": "Vaccination camp tomorrow in Ward 12. Message us for details.",
  "target_location": "Ward 12"
}
```

**GET /api/analytics/queries**
- Query params: tenant_id (auto-scoped), start_date, end_date
- Response:
```json
{
  "total_queries": 150,
  "answered_queries": 120,
  "unanswered_queries": 30,
  "automated_rate": 0.70,
  "top_queries": [
    {"query": "vaccination camp", "count": 45, "language": "hi"},
    {"query": "power outage", "count": 30, "language": "en"}
  ],
  "language_distribution": {
    "hi": 60,
    "en": 50,
    "ta": 40
  }
}
```

**GET /api/analytics/unanswered**
- Weekly digest of unanswered queries (tenant-scoped)
```json
{
  "week": "2026-01-19 to 2026-01-25",
  "unanswered_queries": [
    {
      "query": "garbage collection schedule",
      "count": 37,
      "locations": ["Ward 5", "Ward 12"],
      "languages": ["hi", "en"]
    }
  ]
}
```

**GET /api/analytics/broadcast-coverage**
- Map-based broadcast coverage (tenant-scoped)
```json
{
  "tenant_id": "uuid",
  "coverage": [
    {
      "location": "Ward 12",
      "boundary": {"type": "Polygon", "coordinates": [...]},
      "sent_count": 150,
      "success_rate": 0.95
    }
  ]
}
```

---

## 4. Data Flow

### 4.1 Document Ingestion Flow

```
Admin uploads document (PDF/DOCX/JPG/PNG)
    ↓
Store original file in object storage
    ↓
If image (JPG/PNG):
  → Send to cloud OCR service
  → Extract text
  → Mark as ocr_processed
    ↓
If PDF/DOCX:
  → Parse document (extract text)
    ↓
Validate and mark as draft
    ↓
Admin previews/simulates
    ↓
Admin approves
    ↓
Chunk text (~500 tokens per chunk)
    ↓
Generate embeddings (Cloud LLM)
    ↓
Store in embeddings table (with tenant_id)
    ↓
Document ready for retrieval
```

**Chunking Strategy:**
- Split by paragraph first
- If paragraph > 500 tokens, split by sentence
- Preserve metadata (tenant_id, location, validity) with each chunk
- Store chunk_index for ordering

**OCR Strategy:**
- Cloud OCR service processes images during upload
- Extracted text stored in notices.content
- Original image stored in object storage for reference
- Images are not directly searchable (only extracted text)

---

### 4.2 Query Processing Flow

```
User sends WhatsApp message (any language)
    ↓
Twilio webhook → FastAPI endpoint
    ↓
Extract: phone_number, message, location, language
    ↓
Check session context in Redis (last 5 min)
    ↓
Classify: tenant keywords, location
    ↓
Check response cache in Redis (tenant + location + intent)
    ↓
If cached → return cached response (in same language)
    ↓
If not cached:
    ↓
Query vector DB:
  - Filter by tenant_id (strict isolation)
  - Filter by location (if provided)
  - Filter by validity (not expired)
  - Filter by status (approved only)
  - Vector similarity search
    ↓
Retrieve top 3-5 chunks
    ↓
If no chunks found:
  → Respond: "No verified information available"
  → Provide tenant contact
  → Log as unanswered query (with tenant_id)
    ↓
If chunks found:
  → Pass to Cloud LLM with system prompt
  → LLM detects query language and responds in same language
  → Generate response
  → Post-check for forbidden keywords
  → Cache response in Redis
  → Send via Twilio
    ↓
Log query and response (with tenant_id, language)
```

---

### 4.3 Broadcast Flow

```
Admin triggers broadcast (tenant-scoped)
    ↓
Select target users:
  - Subscribed to tenant
  - Location matches (if specified)
  - Interacted in last 90 days
  - Not opted out
    ↓
Send via WhatsApp Channel (one message)
    ↓
Log broadcast (tenant_id, sent_count, failed_count)
    ↓
Update map-based coverage metrics
```

**Map-Based Broadcast Coverage:**
- Visual representation of ward/area boundaries
- Overlay showing broadcast reach per location
- Success rate metrics per ward/area
- No real-time user location tracking (privacy-first)

---

## 5. RAG Pipeline Design

### 5.1 Retrieval Query

```sql
SELECT 
    e.id,
    e.chunk_text,
    e.embedding <=> $1 AS distance,
    n.title,
    n.location,
    t.name AS tenant_name
FROM embeddings e
JOIN notices n ON e.notice_id = n.id
JOIN tenants t ON e.tenant_id = t.id
WHERE 
    n.publish_status = 'approved'
    AND (n.validity_end IS NULL OR n.validity_end > NOW())
    AND e.tenant_id = $2  -- Strict tenant isolation
    AND ($3 IS NULL OR e.location = $3)
    AND t.is_active = TRUE
ORDER BY e.embedding <=> $1
LIMIT 5;
```

Parameters:
- $1: query embedding (vector)
- $2: tenant_id (required for isolation)
- $3: location (optional)

### 5.2 Cloud LLM Prompt Template

```
System: You are 'Asila, an official information assistant. Answer questions using ONLY the provided context. Do not diagnose, speculate, or provide advice beyond official guidance. If the context does not contain sufficient information, say "No verified information is available."

IMPORTANT: Respond in the SAME LANGUAGE as the user's question. If the user asks in Hindi, respond in Hindi. If in Tamil, respond in Tamil. If in English, respond in English.

Context:
{retrieved_chunks}

User Question: {user_query}

Answer (in the same language as the question):
```

### 5.3 Multi-Language Support
- LLM automatically detects query language
- Generates response in same language
- No separate translation service needed
- Supported languages: Hindi, Tamil, English, Telugu, Bengali, Marathi, etc.
- Language detection stored in queries table for analytics

### 5.4 Response Post-Processing

**Forbidden Keywords Check:**
- Medical diagnosis terms: "you have", "diagnosed with", "treatment for"
- Impersonation: "I am from", "official statement"
- Speculation: "might be", "probably", "I think"

If detected → reject response → fallback to tenant contact

### 5.5 Redis Caching Strategy

**Cache Key Structure:**
```
cache:{tenant_id}:{location}:{intent_hash}:{language}
```

**Example:**
```
cache:uuid-123:ward-12:abc123:hi -> {"response": "...", "chunks": [...]}
```

**Cache Invalidation:**
- TTL: 24 hours
- Manual invalidation when notice is updated
- Per-tenant cache isolation

---

## 6. Technology Stack

### 6.1 Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Async**: asyncio, httpx
- **Database**: PostgreSQL 15+ with pgvector extension
- **Cache**: Redis (mandatory, self-hosted or managed)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **OCR**: Cloud OCR service (e.g., Google Cloud Vision, Azure Computer Vision)

### 6.2 Frontend
- **Framework**: React 18
- **UI Library**: Material-UI or Tailwind CSS
- **State Management**: React Context or Zustand
- **HTTP Client**: Axios
- **Maps**: Leaflet or Mapbox for broadcast coverage visualization

### 6.3 AI/ML
- **LLM**: Cloud-based LLM service (provider-agnostic)
- **Embeddings**: Cloud-based embedding service (1536 dimensions)
- **Vector DB**: pgvector (PostgreSQL extension)
- **Multi-language**: Handled by LLM automatically

### 6.4 Messaging
- **WhatsApp**: Twilio WhatsApp Business API
- **Channels**: WhatsApp Channels (manual setup)

### 6.5 Infrastructure
- **Deployment**: Docker containers (cloud-agnostic)
- **Database**: PostgreSQL (any managed service or self-hosted)
- **Cache**: Redis (any managed service or self-hosted)
- **Storage**: Object storage (S3-compatible)
- **Logging**: Structured JSON logs
- **Monitoring**: Application metrics

### 6.6 Development Tools
- **Version Control**: Git
- **Package Management**: Poetry (Python), npm (React)
- **Testing**: pytest (backend), Jest (frontend)
- **Linting**: ruff (Python), ESLint (React)
- **Containerization**: Docker, Docker Compose

---

## 7. Security Design

### 7.1 Authentication & Authorization
- JWT-based auth for admin dashboard
- Role-based access control per tenant (admin, content_manager)
- No citizen authentication (phone number as ID)
- System admin can access all tenants

### 7.2 Multi-Tenant Data Isolation
- PostgreSQL Row-Level Security (RLS) policies
- Each query scoped to tenant_id
- Strict tenant isolation in all tables
- No cross-tenant data leakage

### 7.3 Data Protection
- Encrypted data in transit (HTTPS, TLS)
- Minimal PII storage (phone number only)
- 30-90 day log retention
- No sensitive data in logs
- Tenant data cannot be accessed by other tenants

### 7.4 Rate Limiting
- Per phone number: 10 messages/hour (Redis-based)
- Per admin user: 100 API calls/minute
- Per tenant: configurable limits

### 7.5 Input Validation
- Sanitize all user inputs
- Validate file uploads (type, size)
- Prevent SQL injection (parameterized queries)
- Prevent XSS (escape outputs)
- OCR output validation

---

## 8. Deployment Architecture

### 8.1 Cloud-Agnostic Design

```
┌─────────────────────────────────────────────────────┐
│                  Load Balancer                       │
│              (Any cloud provider)                    │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│            Container Orchestration                   │
│         (Docker Compose / Kubernetes)                │
│                                                      │
│  ┌──────────────┐         ┌──────────────────────┐ │
│  │   FastAPI    │────────▶│   PostgreSQL         │ │
│  │   Backend    │         │   (pgvector)         │ │
│  │  (Container) │         │   (Managed/Self)     │ │
│  └──────────────┘         └──────────────────────┘ │
│         │                                            │
│         ▼                                            │
│  ┌──────────────┐         ┌──────────────────────┐ │
│  │    Redis     │         │  Object Storage      │ │
│  │    Cache     │         │  (S3-compatible)     │ │
│  │ (Mandatory)  │         │  (Documents)         │ │
│  └──────────────┘         └──────────────────────┘ │
│                                                      │
│  ┌──────────────┐         ┌──────────────────────┐ │
│  │  React App   │         │   Cloud LLM API      │ │
│  │  (Static)    │         │   (External)         │ │
│  └──────────────┘         └──────────────────────┘ │
│                                                      │
│  ┌──────────────┐                                   │
│  │  Cloud OCR   │                                   │
│  │  (External)  │                                   │
│  └──────────────┘                                   │
└─────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌──────────────────┐         ┌──────────────────────┐
│  Twilio WhatsApp │         │  Admin Dashboard     │
│  (Webhook)       │         │  (CDN/Static Host)   │
└──────────────────┘         └──────────────────────┘
```

### 8.2 Environment Setup

**Development**
- Local PostgreSQL with pgvector (Docker)
- Local Redis (Docker)
- Local FastAPI server
- Local React dev server
- Twilio sandbox for testing
- Mock OCR service or test API

**Staging**
- Docker Compose deployment
- Managed PostgreSQL (small instance)
- Managed Redis (small instance)
- Object storage bucket
- Twilio test number
- Cloud OCR test API

**Production**
- Container orchestration (Kubernetes or managed containers)
- Managed PostgreSQL (multi-AZ, replicas)
- Managed Redis (with persistence)
- Object storage with versioning
- CDN for admin dashboard
- Twilio production number
- Cloud OCR production API
- Multi-tenant monitoring

---

## 9. Cost Optimization

### 9.1 WhatsApp Cost Strategy
- **Broadcasts**: Use WhatsApp Channels (one message, unlimited views)
- **1-to-1 Queries**: Use Twilio (pay per message)
- **Estimated Cost**:
  - Channel post: ~$0 (free for public channels)
  - 1-to-1 message: ~$0.005 per message
  - 1000 queries/day = $5/day = $150/month

### 9.2 LLM Cost Strategy
- **Embeddings**: One-time cost per document
  - Cloud embeddings: ~$0.0001 per 1K tokens
  - 1000 documents × 500 tokens = $0.05
- **LLM**: Per-query cost
  - Cloud LLM: ~$0.0008 per 1K input tokens, ~$0.0016 per 1K output tokens
  - Average query: 2K input + 500 output = ~$0.0024
  - 1000 queries/day = $2.40/day = $72/month
- **Redis Caching**: Reduces LLM calls by ~50%
  - Effective cost: ~$36/month

### 9.3 OCR Cost Strategy
- **Cloud OCR**: Pay per image
  - ~$1.50 per 1000 images
  - 100 images/month = $0.15/month
- **One-time cost**: OCR runs only during upload

### 9.4 Infrastructure Cost (Estimated)
- PostgreSQL (managed, medium): ~$60/month
- Redis (managed, small): ~$30/month
- Object storage (100 GB): ~$10/month
- Compute (containers): ~$50/month

### 9.5 Total Estimated Cost (MVP)
- WhatsApp: $150/month
- LLM: $36/month (with caching)
- OCR: $0.15/month
- Database: $60/month
- Redis: $30/month
- Storage: $10/month
- Compute: $50/month
- **Total**: ~$336/month for 1000 queries/day

### 9.6 Multi-Tenant Scaling
- Cost per tenant: ~$10-20/month (incremental)
- Shared infrastructure reduces per-tenant cost
- 10 tenants: ~$450/month total

---

## 10. Implementation Plan

### 10.1 Phase 1: Core Backend & Multi-Tenancy (Days 1-3)
- Set up FastAPI project structure
- Design and create database schema (with tenants table)
- Implement multi-tenant middleware and RLS policies
- Implement admin API endpoints (CRUD for notices)
- Implement document parser (PDF, DOCX)
- Integrate cloud OCR service for images
- Implement chunking logic
- Set up Redis for caching

### 10.2 Phase 2: RAG Pipeline (Days 4-5)
- Integrate cloud LLM for embeddings
- Write embeddings to PostgreSQL (with tenant_id)
- Implement vector similarity search (tenant-scoped)
- Integrate cloud LLM for response generation
- Implement response caching in Redis
- Implement guardrails and post-processing
- Test multi-language support
- Test retrieval accuracy

### 10.3 Phase 3: WhatsApp Integration (Days 6-7)
- Set up Twilio account and WhatsApp number
- Implement webhook endpoint
- Implement query processor (with tenant routing)
- Implement response sender
- Test end-to-end flow
- Test multi-language queries

### 10.4 Phase 4: Admin Dashboard (Day 8)
- Set up React project
- Implement multi-tenant login page
- Implement document upload UI (with OCR support)
- Implement preview/simulation tool
- Implement broadcast trigger UI
- Implement basic analytics dashboard
- Implement map-based broadcast coverage (ward/area boundaries)

### 10.5 Phase 5: Testing & Polish (Day 9)
- End-to-end testing (all tenants)
- Multi-tenant isolation testing
- Multi-language testing
- OCR testing
- Load testing (Redis caching)
- Bug fixes
- Documentation
- Demo preparation

---

## 11. Monitoring & Observability

### 11.1 Key Metrics
- **Query Metrics**:
  - Total queries per hour/day (per tenant)
  - Answered vs unanswered queries (per tenant)
  - Average response latency
  - Redis cache hit rate
  - Automated response rate (target: 70%)
  - Multi-language query distribution
- **LLM Metrics**:
  - API call count (per tenant)
  - Average latency
  - Error rate
  - Cost per day (per tenant)
- **System Metrics**:
  - CPU/memory usage
  - Database connections
  - Redis memory usage
  - Webhook response time
  - OCR processing time
- **Multi-Tenant Metrics**:
  - Active tenants
  - Queries per tenant
  - Cost per tenant

### 11.2 Alerts
- Vector DB unavailable (critical)
- LLM error rate > 5% (warning)
- Redis unavailable (critical)
- Webhook failures > 10/hour (warning)
- Response latency > 5s (warning)
- OCR service unavailable (warning)
- Tenant isolation breach (critical)

### 11.3 Logging Strategy
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Log retention: 30 days
- Sensitive data redaction (phone numbers masked)
- Tenant ID in all logs for isolation
- Language detection logged for analytics

---

## 12. Testing Strategy

### 12.1 Unit Tests
- Document parser
- Chunking logic
- Query classifier
- Response post-processor

### 12.2 Integration Tests
- Database operations
- Bedrock API calls
- Twilio webhook handling
- Cache operations

### 12.3 End-to-End Tests
- Upload document → query → response flow
- Broadcast trigger → delivery
- Admin preview/simulation

### 12.4 Load Tests
- 100 concurrent queries
- 1000 queries in 1 hour
- Database connection pooling

---

## 13. Future Enhancements (Post-MVP)

### 13.1 Phase 2 Features
- Voice message handling
- Video content support
- Bulk document upload
- Scheduled broadcasts
- Advanced analytics (heatmaps, trends)
- White-label customization per tenant
- Custom branding per tenant

### 13.2 Phase 3 Features
- ML-based intent classification
- Semantic verification of responses
- A/B testing for response templates
- Citizen feedback loop (thumbs up/down)
- Integration with existing government systems
- Cross-tenant analytics (system admin only)
- Advanced map features (heat maps, real-time)

### 13.3 Scalability Improvements
- Multi-region deployment
- Read replicas for database
- CDN for static assets
- Redis cluster for high availability
- Kubernetes for orchestration
- Auto-scaling based on tenant load

---

## 14. Risk Mitigation

### 14.1 Technical Risks
- **Risk**: Bedrock unavailable
  - **Mitigation**: Fallback to cached responses, graceful error messages
- **Risk**: Vector DB performance degradation
  - **Mitigation**: Index optimization, query optimization, read replicas
- **Risk**: Twilio rate limits
  - **Mitigation**: Queue messages, retry logic, monitor usage

### 14.2 Operational Risks
- **Risk**: Misinformation propagation
  - **Mitigation**: Manual approval workflow, strict guardrails, audit logs
- **Risk**: System abuse (spam)
  - **Mitigation**: Rate limiting, phone number blocking, anomaly detection
- **Risk**: Data breach
  - **Mitigation**: Minimal PII storage, encryption, access controls

### 14.3 Business Risks
- **Risk**: Low citizen adoption
  - **Mitigation**: QR code campaigns, official endorsements, user education
- **Risk**: Department resistance
  - **Mitigation**: Easy-to-use dashboard, training, visible ROI (reduced helpline calls)

---

## 15. Success Metrics

### 15.1 Technical Metrics
- 99% uptime
- <2s average response time
- >90% Redis cache hit rate
- <1% error rate
- Multi-tenant isolation verified (zero breaches)

### 15.2 Business Metrics
- 3-5 active tenants in first month
- 100+ active citizens per tenant
- 70%+ repetitive queries automated
- 80%+ queries answered from verified sources
- 50%+ reduction in helpline calls per tenant
- Positive feedback from tenant admins

### 15.3 Quality Metrics
- Zero misinformation incidents
- <5% unanswered queries per tenant
- >4/5 user satisfaction rating
- Multi-language support working (3+ languages)
- OCR accuracy >95%
