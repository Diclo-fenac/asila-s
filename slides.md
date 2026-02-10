Slide 1: Brief about the Idea
Header:

Powered by: AWS | Innovation partner: H2S | Media partner: YOURSTORY

Event: AI for Bharat Hackathon

Main Content:

Title: Brief about the Idea:

Internet Connections vs. WhatsApp Users in India:

970M+ Internet Connections (Total internet connections in India)

800M+ WhatsApp Users (WhatsApp users in India)

Query Handling Comparison:

Asila: 70% Repetitive queries automated

Traditional: 0% Repetitive queries automated

Transforming Governance with 'Asila':

Fragmented Governance: PDFs and scattered portals

Implement 'Asila': Default citizen interface via WhatsApp | Unstructured data to verified responses | Plug-and-play backbone for departments

Digital Governance: Chat and solve government issues

Text Narrative: India has built the world's most robust digital plumbing with 97+ crore internet connections, yet the "last mile" of communication remains broken, trapped in scattered PDFs and prone to viral misinformation.

'Asila is the solution: a department-agnostic, plug-and-play stack that turns WhatsApp into a verified, friction-free communication portal. By automating up to 70% of repetitive citizen queries, we've moved beyond bespoke pilots into a scalable SaaS model for the state. As India's digital economy heads toward 20% of GDP, 'Asila is the essential layer that turns connectivity into trust, ensuring every citizen has a verified answer in their pocket, 24/7.

Beyond digitizing government services, our platform offers a secure 'verified channel' for local corporations and businesses to reach their specific community clusters.

Slide 2: Comparison with Competitors & USP
Comparison Table: | Feature | vs. Portals | vs. Existing Bots | vs. Generic AI | vs. Manual/SMS | | :--- | :--- | :--- | :--- | :--- | | Interaction | Natural Language | Doing one thing perfectly | Constrained RAG Pipeline | Free WhatsApp Channels | | Problem Solved | Information Graveyards | Doing everything poorly | Hallucinations | Character-limited, expensive SMS |

Section: How will it be able to solve the problem?

Information Asymmetry: Meets citizens where they are (WhatsApp) instead of forcing them to visit obscure websites.

The Scale Problem: As it is service-agnostic, it works with all departments as well as businesses.

The Trust Problem: Builds credibility through source citations for every response, prioritizing accuracy over generative 'guessing' (e.g., providing links to official PDFs).

The Feedback Loop: Logs every "unanswered" query to tell departments exactly what information gaps to fill.

Section: USP: Building Trust Through Innovation

Honest Bot: Refuses to guess, ensuring accurate and trustworthy information.

Built for Reality: Accessible to non-technical users and feature phone owners.

Economic Disruption: Faster deployment and lower costs than traditional apps.

Dual-Channel Architecture: Combines mass broadcast and direct query for comprehensive communication.

Result: Trustworthy Communication System

Slide 3: List of features offered by the solution
For Citizens:

Privacy-First Trust: Builds confidence through verified source citations.

Proactive & Hyper-Local Updates: Delivers location-specific broadcasts directly to users.

Instant & Accurate Knowledge: Provides 24/7 instant answers to government queries.

Zero-Friction Experience: Requires no registration or complex navigation.

Core Infrastructure (Connecting the two):

Automated Document Parsing

WhatsApp Query Handling

Multi-Language Support

Verified Channel

For Services:

Rapid Deployment: Quick and cost-effective implementation.

Actionable Analytics: Identification of information gaps.

Dynamic Content: Centralized dashboard for document management.

Operational Scale: Automation of repetitive queries.


Technical Architecture
The system is built on a scalable cloud-native stack primarily utilizing AWS services to handle citizen queries and administrative management.

Layered Infrastructure
Frontend Layer: Department officials access a management interface served via Amazon CloudFront and hosted on S3.

Application Layer: * Entry Point: Citizen queries enter through the Twilio WhatsApp API, which triggers a Webhook to the API Gateway.

Processing: An Application Load Balancer (ALB) routes traffic to services running on AWS Fargate.

Caching: MemoryDB for Redis is used for session storage and cache checks to speed up frequent queries.

Data & AI Layer:

Document Storage: Official documents are stored in Amazon S3.

Search: Amazon RDS (PostgreSQL) with vector capabilities handles the retrieval of relevant document chunks.

Intelligence: Amazon Bedrock provides AI/ML services for generating embeddings and synthesizing final responses.

Monitoring: Amazon CloudWatch tracks system performance and logs.

Query Processing Workflow
The backend follows a 9-step pipeline to transform a citizen's message into a verified answer:

Ingestion: A FastAPI webhook receives the message payload.

Extraction: Key details like phone number, intent, and location (e.g., "Ward 12") are parsed.

Context Check: Redis retrieves the last known location or session state.

Classification: The system identifies the user's intent and the relevant government department.

Cache Check: If a valid response already exists for the query, it is sent immediately to save time and cost.

Vector Search: If no cache hit, the system queries PostgreSQL using pgvector to find document chunks similar to the query.

Retrieval: The top 3–5 most relevant chunks are retrieved.

Generation: Amazon Bedrock synthesizes an answer using a system prompt, the retrieved context, and the user's question.

Guardrails: Post-processing ensures the response is safe, grounded in official data, and free of medical advice or impersonation.

User Interface & Dashboards
The solution provides tailored interfaces for different administrative levels to manage the "last mile" of communication.

1. Department System Admin
Overview: Displays total queries, automated responses, and active broadcasts.

Notice Management: Allows officials to upload new notices (PDF/JPG) and preview how they will appear on WhatsApp before publishing.

Analytics: Tracks "Recent Activity" and system status for the WhatsApp API and AI Engine.

2. City Admin Dashboard
Broadcast Management: Features a map-based interface to manage and monitor public information campaigns with reach and success rate metrics.

Unanswered Queries: A critical feedback loop that identifies "Knowledge Gaps"—queries the AI couldn't answer—allowing admins to manually broadcast a resolution or update documentation.

3. Citizen Interface (WhatsApp)
Natural Interaction: Citizens interact via a standard chat interface.

Automated Flow: The bot provides greetings, asks for contextual clarification (like location), and delivers precise information (e.g., vaccination camp details) with timestamps.