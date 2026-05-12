# Nistula Technical Assessment

**Production-ready AI-powered hospitality messaging backend** built with FastAPI and Claude AI.

The platform receives inbound guest messages from multiple channels, normalizes them into a unified schema, classifies guest intent, generates AI-assisted replies, and determines operational actions using confidence scoring.

## Key Capabilities

- **Multi-Channel Intake**: WhatsApp, Booking.com, Airbnb, Instagram, Direct
- **Unified Schema**: All messages normalized with UUID traceability
- **Intent Classification**: Rule-based detection (availability, pricing, check-in, special request, complaint, general inquiry)
- **AI-Assisted Drafting**: Anthropic Claude with hospitality-safe grounding
- **Confidence Routing**: Auto-send (>0.85), agent-review (0.60–0.85), escalate (<0.60 or complaints)
- **Production-Grade**: Type hints, async/await, error handling, PostgreSQL schema, test payloads

## Features

- FastAPI async webhook endpoint: `POST /webhook/message`
- Health endpoint: `GET /health`
- Pydantic request/response validation
- Anthropic Claude SDK integration (`claude-sonnet-4-20250514`)
- Environment-driven secret management via `.env`
- PostgreSQL schema with constraints, indexes, and audit timestamps
- Test payload bundle and `curl` examples

## Tech Stack

- Python 3.11+
- FastAPI
- Pydantic v2
- Anthropic Python SDK
- PostgreSQL (schema included in SQL)
- python-dotenv / pydantic-settings

## Folder Structure

```text
nistula-technical-assessment/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── classifier.py
│   ├── claude_service.py
│   ├── confidence.py
│   ├── prompts.py
│   ├── utils.py
│   └── constants.py
├── tests/
│   ├── test_payloads.json
│   └── sample_requests.md
├── schema.sql
├── thinking.md
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
└── run.sh
```

## Setup Instructions

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create environment file:

```bash
cp .env.example .env
```

4. Set your Anthropic key in `.env`:

```env
ANTHROPIC_API_KEY=your_real_key
```

## Running Locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or:

```bash
bash run.sh
```

API docs will be available at:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

## Environment Variables

- `ANTHROPIC_API_KEY`: required secret for Anthropic API access.

## API Documentation

### API Preview

Access interactive Swagger documentation at:
```
http://localhost:8000/docs
```

Interactive features:
- Live endpoint testing with request/response examples
- Automatic schema validation and type checking
- Full model documentation with field constraints

### Health Check

`GET /health`

Response:

```json
{
  "status": "ok",
  "service": "nistula-technical-assessment"
}
```

### Inbound Message Webhook

`POST /webhook/message`

Request body:

```json
{
  "source": "whatsapp",
  "guest_name": "Rahul Sharma",
  "message": "Is the villa available from April 20 to 24? What is the rate for 2 adults?",
  "timestamp": "2026-05-05T10:30:00Z",
  "booking_ref": "NIS-2024-0891",
  "property_id": "villa-b1"
}
```

Success response (200 OK):

```json
{
  "message_id": "d2091e64-4fd5-4ef7-a7ec-c2e0d80e9b11",
  "query_type": "pre_sales_availability",
  "drafted_reply": "Hi Rahul! Great news—Villa B1 is available from April 20-24. The base rate is INR 18,000 per night for up to 4 guests, with INR 2,000 per night for each additional guest. For 2 adults, that would be INR 18,000 per night. Feel free to reach out with any other questions!",
  "confidence_score": 0.93,
  "action": "auto_send"
}
```

### Error Response Shape

```json
{
  "error": "validation_error",
  "detail": "...",
  "request_id": "f6f8d250-efab-4a54-a07d-4f903fb6032d"
}
```

## Confidence Scoring

Base confidence is intent-driven and adjusted by urgency/ambiguity signals:

- `complaint`: low confidence, always escalated
- factual pre-sales and check-in questions: high confidence
- special requests: medium confidence for agent supervision

Action mapping:

- `auto_send` for score > 0.85
- `agent_review` for 0.60 to 0.85
- `escalate` for < 0.60 or any complaint

## Architecture Decisions

- Clean modular design separating API, schemas, classification, prompt engineering, AI integration, and confidence policy.
- Deterministic rule-based classifier for transparent behavior and fast runtime.
- Prompt grounded with strict property context to reduce hallucination risk.
- Explicit AI timeout and upstream error mapping into API-safe status codes.

## Assumptions

- Single-property context is fixed to Villa B1 for this assessment.
- Inbound payload always includes booking reference and property ID.
- AI output is treated as draft text; human override is expected in escalations.

## Error Handling Strategy

- Pydantic model validation for payload correctness and source restrictions.
- FastAPI validation handler for structured 422 responses.
- Claude timeout mapped to 504, provider errors mapped to 502.
- Generic exception boundary returns consistent 500 response body.

## Future Improvements

- **Async Processing**: Redis queue for offloading long-running inference tasks
- **Persistent Storage**: SQLAlchemy ORM layer with PostgreSQL migrations
- **Conversation Memory**: Maintain multi-turn guest context within conversations table
- **Semantic Classification**: Embed messages and use similarity search for intent refinement
- **Multi-Property Support**: Dynamic property context loading from database
- **Agent Dashboard**: React UI for reviewing queued messages, editing drafts, and tracking metrics
- **Authentication & Rate Limiting**: JWT tokens, per-guest/property API quotas
- **Observability**: OpenTelemetry spans, Prometheus metrics, Grafana dashboards
- **Retry Strategy**: Exponential backoff for Claude API failures
- **Webhook Security**: HMAC signature verification for inbound sources
- **Conversation Summarization**: Auto-generate guest sentiment and issue summaries
- **Multi-Language Support**: Translate inbound messages and draft replies
- **Sentiment Analysis**: Detect guest satisfaction and escalate proactively
- **A/B Testing**: Test multiple Claude prompts and measure response quality

## Future Improvements

- Add async persistence layer with SQLAlchemy and Postgres integration.
- Add unit/integration tests with pytest and mocked Anthropic SDK.
- Introduce rate limiting and idempotency keys for webhook hardening.
- Add multilingual support and response style profiles by channel.
- Add observability stack (OpenTelemetry traces, metrics, alerting).
