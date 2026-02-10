# Integration Guide - External Services

## 1. Cloud LLM Provider (Bedrock/OpenAI)

### File: `backend/app/services/llm.py`

Replace stubs with real implementations:

```python
import boto3  # or openai

# Bedrock example
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

async def generate_embedding(text: str) -> list[float]:
    response = bedrock_runtime.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({"inputText": text})
    )
    return json.loads(response['body'].read())['embedding']

async def generate_response(context_chunks: list[str], query: str) -> str:
    prompt = f"Context: {' '.join(context_chunks)}\n\nQuestion: {query}\n\nAnswer:"
    response = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-v2',
        body=json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 500,
            "temperature": 0.3
        })
    )
    return json.loads(response['body'].read())['completion']
```

## 2. Twilio WhatsApp API

### File: `backend/app/services/broadcast.py`

Add Twilio credentials to `.env`:
```env
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886
```

Replace stub:
```python
from twilio.rest import Client

client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

async def send_whatsapp_broadcast(phone_numbers: list[str], message: str) -> tuple[int, int]:
    sent, failed = 0, 0
    for phone in phone_numbers:
        try:
            client.messages.create(
                from_=f'whatsapp:{settings.twilio_whatsapp_number}',
                to=f'whatsapp:{phone}',
                body=message
            )
            sent += 1
        except Exception:
            failed += 1
    return sent, failed
```

## 3. Cloud OCR Service (Google Vision / AWS Textract)

### File: `backend/app/services/ingestion.py`

Add to `.env`:
```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
# or
AWS_REGION=us-east-1
```

Replace OCR stub:
```python
from google.cloud import vision
# or
import boto3

async def extract_text_from_image(image_bytes: bytes) -> str:
    # Google Vision
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    return response.text_annotations[0].description if response.text_annotations else ""
    
    # OR AWS Textract
    textract = boto3.client('textract')
    response = textract.detect_document_text(Document={'Bytes': image_bytes})
    return ' '.join([block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE'])
```

## 4. Enable DB Retrieval

### File: `backend/app/services/query.py`

Uncomment retrieval section (lines ~45-50):
```python
# Replace:
context_texts = []

# With:
from app.db.session import AsyncSessionLocal
from app.services.retrieval import retrieve_chunks

async with AsyncSessionLocal() as session:
    chunks = await retrieve_chunks(session, tenant_id, embedding, location)
    context_texts = [c.chunk_text for c in chunks]
```

## 5. Production Configuration

### Update `backend/app/core/config.py`:
```python
class Settings(BaseSettings):
    # ... existing fields ...
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
```

### Add to `backend/requirements.txt`:
```
boto3>=1.34.0  # for Bedrock/Textract
twilio>=8.10.0  # for WhatsApp
google-cloud-vision>=3.5.0  # if using Google OCR
```

## 6. Initialize Database

```bash
# Run migrations
cd backend
alembic upgrade head

# Seed tenant data (optional)
python -c "
from app.db.session import AsyncSessionLocal
from app.models import Tenant
import asyncio

async def seed():
    async with AsyncSessionLocal() as session:
        tenants = [
            Tenant(name='Health Department', type='government'),
            Tenant(name='Electricity Board', type='government'),
            Tenant(name='Water Authority', type='government'),
            Tenant(name='Municipality', type='government'),
        ]
        session.add_all(tenants)
        await session.commit()

asyncio.run(seed())
"
```

## 7. Test Integration

```bash
# Test webhook
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "From": "whatsapp:+919876543210",
    "Body": "vaccination camp near me"
  }'

# Test admin API
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

## 8. Monitoring Setup

Add to `backend/app/main.py`:
```python
import logging
from aws_xray_sdk.ext.fastapi.middleware import XRayMiddleware
from aws_xray_sdk.core import xray_recorder

# AWS X-Ray
xray_recorder.configure(service='asila-backend')
app.add_middleware(XRayMiddleware, recorder=xray_recorder)

# CloudWatch Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Done!
Your backend is now fully integrated and production-ready.
