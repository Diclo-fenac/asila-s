# Requirements Document: 'Asila - WhatsApp-Based Public Information System

## 1. Project Overview

### 1.1 Purpose
Build 'Asila, a WhatsApp-based public information system for government departments, corporations, and service providers to distribute verified information at scale and answer citizen queries using only approved data sources. A department-agnostic, plug-and-play stack that turns WhatsApp into a verified, friction-free communication portal.

### 1.2 Core Principles
- **Broadcast information once via Channels. Answer questions only when users ask.**
- **Use AI sparingly and reuse results.**
- **Optimize for WhatsApp cost, not AI cost.**
- **No misinformation, no speculation, no diagnosis.**
- **Multi-tenancy: Each department/business operates independently.**

### 1.3 Target Users
- **Citizens**: Receive broadcasts and ask queries via WhatsApp in their preferred language
- **Department Officials**: Upload notices (including images), trigger broadcasts, view analytics
- **Business/Corporate Users**: Same capabilities as departments, separate tenant
- **System Admins**: Manage tenants, monitor system health

### 1.4 MVP Scope
- 3-5 tenants (departments or businesses: Health, Electricity, Municipality, optional Telecom/Corporate)
- Multi-tenancy architecture (each tenant isolated)
- Thousands of users per channel
- Hundreds of daily queries
- Multi-language support via LLM
- OCR for image-based documents
- 9-day working prototype timeline

---

## 2. Functional Requirements

### 2.1 User Onboarding & Identity

**FR-2.1.1: Citizen Discovery**
- Citizens discover the bot via:
  - QR codes on posters, notices, camps, bills
  - Official government messages with WhatsApp number
- No search or invite-based discovery

**FR-2.1.2: Identity Verification**
- Phone number is sufficient identity
- No Aadhaar, voter ID, or formal verification
- System is for information delivery, not entitlements

**FR-2.1.3: Location Handling**
- Location is user-provided, explicit, and optional
- Methods:
  - User types ward/area/pincode
  - User shares WhatsApp location
- No inference from telecom data

**FR-2.1.4: User Profiles**
- Minimal profile storage:
  - `phone_number` (primary key)
  - `last_known_location` (optional, ephemeral)
  - `subscribed_departments` (optional)
  - `last_interaction_timestamp`
- Messages are mostly stateless

**FR-2.1.5: Location Memory**
- Remember location for session window (5-10 minutes)
- Forget after session ends
- Support location aliases (e.g., "Sector 5" = "Ward 12") via lookup table

---

### 2.2 Broadcast & Opt-in

**FR-2.2.1: Broadcast Targeting**
- Only users who have interacted at least once AND opted in receive broadcasts
- Targeting filters:
  - By department
  - By location (ward, area)
  - By subscription

**FR-2.2.2: Subscription Management**
- Users can subscribe/unsubscribe via simple commands:
  - "Subscribe health"
  - "Unsubscribe electricity"
  - "Stop all"
- No UI or menus for MVP

**FR-2.2.3: Inactive User Handling**
- If no interaction for 90 days, stop broadcasts automatically

**FR-2.2.4: Delivery Tracking**
- Track:
  - Message sent
  - Message failed
- No read receipts for MVP

**FR-2.2.5: Broadcast Trigger**
- Manual trigger only
- Uploading a document does NOT auto-send messages
- Admin must explicitly click "Send broadcast"
- Broadcast includes concise message + CTA: "Message us for details"

---

### 2.3 Conversation Flow

**FR-2.3.1: Context Memory**
- Short-term context only
- Remember last 1-2 messages
- Context expires after 5 minutes
- No long conversations

**FR-2.3.2: Query Refinement**
- Support one refinement step only
- Pattern:
  - User: "vaccination"
  - Bot: "Which ward are you in?"
  - User: "Ward 5"
  - Bot: returns answer
- No open-ended conversations

**FR-2.3.3: Clarifying Questions**
- Ask one clarifying question max (e.g., "Which ward are you in?")
- If still unclear after that, respond: "No verified information available"
- Never guess

**FR-2.3.4: Multiple Questions**
- Out of scope for MVP
- If detected:
  - Answer the most relevant one
  - Or ask user to ask one question at a time

---

### 2.4 Document Management

**FR-2.4.1: Document Upload**
- Admin dashboard upload only
- Supported formats: PDF, DOCX, JPG, PNG, plain text
- OCR processing for image files (JPG, PNG) to extract text
- Images are not directly searchable, only extracted text is indexed
- No email ingestion, no public API ingestion

**FR-2.4.2: Document Trust Model**
- Each document has:
  - `source_type`: restricted enum (official_notice, advisory, service_notice)
  - `approved_by`: role or department
  - `publish_status`: draft, approved, archived
- Only documents marked "approved" are indexed for retrieval
- Departments can choose from restricted enum based on their role

**FR-2.4.3: Document Validation**
- Manual validation only
- Admin uploads and explicitly marks as publishable
- No auto-publish, no scraping

**FR-2.4.4: Document Versioning**
- Replace current document
- Archive old version with timestamp
- Only latest version is indexed
- Archived documents are NOT used in retrieval

**FR-2.4.5: Historical Queries**
- If user asks historical questions, respond: "Historical information is not available via this channel"

**FR-2.4.6: OCR Support**
- Cloud-based OCR service for image processing
- Supported formats: JPG, PNG
- OCR runs during document upload
- Extracted text is chunked and embedded like regular documents
- Original images stored for reference but not searchable

---

### 2.5 Query Handling & RAG

**FR-2.5.1: Intent Classification**
- No ML-based intent classification for MVP
- Use lightweight keyword extraction:
  - Parse message for department keywords (vaccination, electricity, water, garbage)
  - Parse message for location mentions
  - Route based on keywords

**FR-2.5.2: Retrieval Strategy**
- Hybrid search (keyword + vector):
  - Keyword filter by department and location
  - Vector similarity inside filtered set
- Metadata filtering:
  - Department
  - Location
  - Validity period (exclude expired notices)
  - Archived status (exclude archived)

**FR-2.5.3: Response Generation**
- Pass top 3-5 retrieved chunks to Amazon Bedrock
- System prompt includes:
  - "Answer only using provided context"
  - "Do not diagnose"
  - "Do not speculate"
  - "Do not provide advice beyond official guidance"
- If no relevant document found, respond: "No verified information is available on this topic from official sources. Please contact [department contact]"

**FR-2.5.4: Guardrails**
- Post-check response for:
  - Unsupported claims
  - Forbidden keywords (medical diagnosis, impersonation)
- Reject if detected

**FR-2.5.5: Response Caching**
- Cache by department + location + intent
- Cache after first Bedrock call
- Threshold: worth it after ~20 repeated queries/day

**FR-2.5.6: Latency Targets**
- Retrieval: under 500ms
- End-to-end response: under 2 seconds

---

### 2.6 Error Handling & Fallbacks

**FR-2.6.1: Vector DB Down**
- Return static response: "The service is temporarily unavailable. Please try again later."
- Do not retry endlessly

**FR-2.6.2: Bedrock Slow or Unavailable**
- Fallback order:
  1. Cached responses for common queries
  2. Static department contact info
  3. Graceful failure message
- Never block WhatsApp webhook

**FR-2.6.3: Gibberish or Spam**
- Detect low confidence or non-language input
- Respond once with help text
- Ignore repeated spam
- Rate limiting: 10 messages per hour per number

---

### 2.7 Department Contacts & Escalation

**FR-2.7.1: Contact Storage**
- Store in PostgreSQL database, separate table
- Fields:
  - `department`
  - `phone`
  - `email`
  - `office_address`
  - `working_hours`

**FR-2.7.2: Contact Options**
- Offer text-only contact info:
  - Phone number
  - Office address
- No live transfers, no ticket creation

**FR-2.7.3: Redirect Tracking**
- Store:
  - Query text
  - Department routed to
  - Reason (no data, out of scope)
- Feeds analytics and improves ingestion

---

### 2.8 Admin Dashboard

**FR-2.8.1: User Roles & Multi-Tenancy**
- Each department/business is a separate tenant
- Tenant isolation: departments cannot see each other's data
- Roles per tenant: admin, content_manager
- System admin can manage all tenants
- 3-5 tenants for MVP

**FR-2.8.2: Upload Format**
- One-by-one upload only
- Bulk upload deferred

**FR-2.8.3: Preview & Simulation**
- Admin can:
  - Choose a location
  - Ask a sample query
  - See exact response
- Default view: final response
- Expandable view: retrieved chunks + source
- Documents cannot be published without preview test

**FR-2.8.4: Department Feedback**
- Departments can see:
  - Queries routed to them
  - Unanswered queries
  - Map-based broadcast coverage (ward/area boundaries)
- No free-form analytics yet

**FR-2.8.5: Map-Based Broadcast Interface**
- Visual map showing ward/area boundaries
- Broadcast coverage overlay
- Reach and success rate metrics per location
- No real-time user location tracking (privacy-first)

---

### 2.9 Analytics & Monitoring

**FR-2.9.1: Metrics**
- For MVP:
  - Total queries per tenant (department/business)
  - Unanswered queries
  - Broadcast sent count
  - Most common query types
  - Automated response rate (target: 70% of repetitive queries)

**FR-2.9.2: Tenant-Specific Analytics**
- Each tenant sees only its own data (strict isolation)
- Cross-tenant views are system admin-only
- No data sharing between tenants

**FR-2.9.3: Reporting**
- Daily batch reports only
- Dashboards can be static charts

**FR-2.9.4: Unanswered Query Feedback Loop**
- Automatic clustering by department + keyword
- Weekly digest per department:
  - Top unanswered queries
  - Count
  - Affected locations
- System flags gaps, does not auto-suggest content

---

### 2.10 Compliance & Security

**FR-2.10.1: Logging**
- Log:
  - Queries
  - Responses
  - Timestamps
- Retention: 30-90 days for MVP

**FR-2.10.2: Sensitive Queries**
- Treat all queries as informational
- If health-related:
  - Add disclaimer
  - No diagnosis
  - Only official guidance

**FR-2.10.3: Rate Limiting**
- Per phone number
- Simple counter in DB or cache

**FR-2.10.4: Impersonation Prevention**
- Only admin dashboard can publish broadcasts
- All documents are source-tagged
- No user-generated content is rebroadcast

---

## 3. Non-Functional Requirements

### 3.1 Performance
- Retrieval latency: <500ms
- End-to-end response: <2 seconds
- Support thousands of users per channel
- Hundreds of daily queries
- Redis caching mandatory for performance

### 3.2 Scalability
- Design assumes:
  - Thousands of users per channel
  - Tens of thousands of broadcast views
  - Hundreds of daily queries
- Multi-tenant architecture supports unlimited tenants
- Millions of queries = future phase

### 3.3 Availability
- Target: 99% uptime for MVP
- Graceful degradation on service failures
- Redis failover support

### 3.4 Security
- No PII storage beyond phone number
- Encrypted data in transit (HTTPS, TLS)
- Tenant data isolation (strict separation)
- Role-based access control per tenant

### 3.5 Maintainability
- Cloud-agnostic design (deploy anywhere)
- Containerized services (Docker)
- Tenants self-serve content, not infrastructure

### 3.6 Multi-Language Support
- LLM handles input/output in multiple languages automatically
- Citizens can query in Hindi, Tamil, English, etc.
- Responses generated in the same language as query
- No separate translation service required

---

## 4. Out of Scope (Deferred)

### 4.1 Deferred Safely
- Voice message handling
- Video content
- Full analytics dashboards (only basic metrics for MVP)
- Complaint handling/ticketing system
- Identity verification (Aadhaar, etc.)
- A/B testing
- Bulk document upload
- Scheduled broadcasts
- Persistent user profiles
- Fuzzy geo-matching
- ML-based intent classification
- Semantic verification of responses
- Real-time alerts for departments
- AI-assisted draft suggestions
- Post-publish monitoring tools
- Full conversational state
- Cross-tenant analytics
- White-label customization

---

## 5. Success Criteria

### 5.1 MVP Success
- 3-5 tenants onboarded (departments/businesses)
- 100+ citizens using the system
- 70%+ repetitive queries automated
- 80%+ queries answered from verified sources
- <2 second average response time
- Zero misinformation incidents
- Multi-language queries handled successfully
- Positive feedback from tenant admins

### 5.2 Prototype Demo Readiness
- Working end-to-end flow:
  - Admin uploads document (PDF/JPG with OCR)
  - Document is chunked and embedded
  - Citizen asks query via WhatsApp (any language)
  - System retrieves and responds in same language
  - Admin views analytics and map-based broadcast coverage
  - Multi-tenant isolation verified
- 9-day timeline

---

## 6. Constraints

### 6.1 Technical Constraints
- Cloud-agnostic design (deploy to any cloud provider later)
- Python + FastAPI backend
- LLM service for embeddings and generation (cloud-based)
- PostgreSQL + pgvector for storage
- Redis for caching (mandatory)
- Cloud OCR service for image processing
- Twilio for WhatsApp integration
- React for admin dashboard
- Docker containers for deployment

### 6.2 Operational Constraints
- Solo developer for MVP
- 9-day prototype timeline
- Cost-conscious design (optimize for WhatsApp cost)
- Multi-tenant architecture from day one

### 6.3 Legal & Compliance Constraints
- No diagnosis or medical advice
- No speculation or unverified information
- No user-generated content propagation
- 30-90 day log retention
- Privacy-first design (minimal PII)
- Strict tenant data isolation
