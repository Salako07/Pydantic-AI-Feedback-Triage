# AI-Powered Customer Feedback Triage Dashboard

A production-ready system that automatically analyzes customer feedback using AI (via PydanticAI), categorizes messages by sentiment, urgency, and topic, and displays results in a real-time dashboard.

## Version 2.0 - Phase 2 Production Enhancements

This version includes comprehensive production features for AI observability, human-in-the-loop corrections, and automated analytics.

## Features

### Phase 1 (Core Features)
- **AI-Powered Analysis**: Uses PydanticAI with pluggable LLM backends (OpenAI, Anthropic, Google Gemini)
- **Structured Output**: Validates AI responses using Pydantic schemas for type-safe results
- **Real-Time Updates**: WebSocket integration pushes new feedback to dashboard instantly
- **Smart Categorization**: Automatically extracts sentiment, urgency, category, summary, and recommended actions
- **Rich Dashboard**: Interactive charts, filters, and detailed ticket views
- **Production Ready**: Docker containerized, tested, with CI/CD pipeline
- **Type Safe**: TypeScript frontend, Pydantic backend

### Phase 2 (Production Enhancements)
- **Observability**: Track AI agent success rate, failures, and error reasons with `agent_success` and `analysis_error` fields
- **Human-in-the-Loop**: Override AI analysis with audit trail - capture field changes, reasons, and reviewer identity
- **Metrics & Analytics**: REST APIs for accuracy metrics, urgency breakdown, and sentiment trends
- **Automated Reports**: Weekly job (APScheduler) computes performance metrics and archives reports
- **Slack Integration**: Real-time alerts for high-urgency feedback and weekly performance summaries
- **Dynamic Prompt Tuning**: Configure bias words, urgency rules, and retry logic via JSON file
- **Demo Deployment**: One-command script to build, start, and seed demo environment

## Tech Stack

**Backend:**
- Python 3.11
- FastAPI (async web framework)
- PydanticAI (AI agent framework)
- MongoDB (document database)
- Motor (async MongoDB driver)
- APScheduler (background jobs) - Phase 2
- Requests (Slack webhooks) - Phase 2

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Recharts (data visualization)
- Axios (HTTP client)

**Infrastructure:**
- Docker + Docker Compose
- GitHub Actions (CI/CD)
- pytest (backend tests)
- Vitest + React Testing Library (frontend tests)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- API key for your chosen LLM provider (OpenAI, Anthropic, or Google)
- (Optional) Slack webhook URL for Phase 2 alerts

### Phase 2 One-Command Deployment (Recommended)

```bash
# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Deploy everything (build, start, seed demo data)
bash deploy_demo.sh
```

This automated script will:
1. Build Docker images
2. Start all services
3. Wait for health checks
4. Seed 10 demo feedback messages
5. Display all access URLs and Phase 2 features

### Manual Deployment

If you prefer manual control:

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-feedback-triage
```

#### 2. Configure Environment

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and set your LLM configuration:

```env
# Choose your LLM provider and add the corresponding API key
LLM_MODEL=openai:gpt-4o
OPENAI_API_KEY=your_actual_api_key_here

# Phase 2: Optional Slack integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Phase 2: Optional job schedule (default: Every Monday 9 AM UTC)
SCHEDULE_CRON_WEEKLY=0 9 * * 1
```

#### 3. Start the Application

```bash
docker compose up --build
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend Dashboard**: http://localhost:5173
- **MongoDB**: localhost:27017

#### 4. Seed Sample Data (Phase 2)

```bash
docker compose exec backend python -m app.seed.seed_demo
```

This populates the database with 10 sample customer feedback messages and 1 demo override.

#### 5. Access the Dashboard

Open your browser to http://localhost:5173

You should see:
- Summary statistics (total messages, high urgency count, negative sentiment %)
- Interactive charts showing category distribution, urgency breakdown, and sentiment trends
- Filterable table of all feedback messages
- Click any row to see full details and AI analysis

**Phase 2 Features:**
- High-urgency feedback triggers Slack alerts (if configured)
- View metrics at http://localhost:8000/api/metrics/accuracy
- Apply human overrides via API or upcoming UI
- Weekly job runs automatically to generate performance reports

## API Documentation

Once running, visit http://localhost:8000/docs for interactive OpenAPI documentation.

### Key Endpoints

**POST /api/feedback**
```json
{
  "customer_name": "John Doe",
  "email": "john@example.com",
  "message": "I can't access my account!"
}
```

Response (201 Created):
```json
{
  "id": "507f1f77bcf86cd799439011",
  "customer_name": "John Doe",
  "email": "john@example.com",
  "message": "I can't access my account!",
  "created_at": "2025-01-15T10:30:00",
  "analysis": {
    "sentiment": "negative",
    "urgency_level": "high",
    "category": "account",
    "summary": "Customer unable to access account",
    "recommended_action": "Immediately investigate account access issue and contact customer"
  }
}
```

**GET /api/feedback**

Query parameters:
- `limit` (default: 50, max: 100)
- `skip` (default: 0)
- `urgency` (low | medium | high)
- `sentiment` (positive | neutral | negative)
- `category` (string)
- `unresolved_only` (boolean)

**GET /api/feedback/{id}**

Returns single feedback by ID.

**WebSocket: /ws/feedbacks**

Connect to receive real-time updates when new feedback is created.

### Phase 2 API Endpoints

**POST /api/feedback/{id}/override**

Apply human override to correct AI analysis:

```json
{
  "field": "sentiment",
  "new_value": "negative",
  "reason": "AI missed sarcastic tone indicating frustration",
  "overridden_by": "reviewer@company.com"
}
```

Response: Updated feedback with override recorded in `overrides` array.

**GET /api/feedback/{id}/overrides**

Returns complete audit trail of all overrides applied to a feedback.

**GET /api/metrics/accuracy**

Returns AI agent accuracy metrics:

```json
{
  "total_processed": 150,
  "total_overridden": 12,
  "overall_accuracy": 0.92,
  "by_category": {
    "billing": 0.88,
    "technical": 0.94,
    "product": 0.90
  }
}
```

**GET /api/metrics/urgency-breakdown**

Returns count by urgency level:

```json
{
  "low": 45,
  "medium": 78,
  "high": 27,
  "total": 150
}
```

**GET /api/metrics/sentiment-trend?days=7**

Returns daily sentiment data for last N days:

```json
[
  {
    "date": "2025-01-15",
    "positive": 12,
    "neutral": 8,
    "negative": 5
  },
  ...
]
```

## Development

### Running Tests

**Backend tests:**
```bash
cd backend
pip install -r requirements.txt
pytest app/tests/ -v
```

**Frontend tests:**
```bash
cd frontend
npm install
npm run test
```

**Linting:**
```bash
# Backend
cd backend
ruff check app/
black app/

# Frontend
cd frontend
npm run lint
```

### Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── schemas.py           # Pydantic models
│   │   ├── models.py            # Data transformation
│   │   ├── db.py                # MongoDB connection
│   │   ├── ai_agent.py          # PydanticAI agent
│   │   ├── services.py          # Business logic
│   │   ├── utils.py             # Utilities
│   │   ├── api/
│   │   │   └── routes_feedback.py  # API routes
│   │   └── tests/               # Backend tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── types/               # TypeScript types
│   │   ├── services/            # API & WebSocket clients
│   │   ├── pages/               # Page components
│   │   ├── components/          # Reusable components
│   │   ├── styles/              # Tailwind CSS
│   │   └── tests/               # Frontend tests
│   ├── Dockerfile
│   └── package.json
├── seed_data/
│   └── seed_feedback.py         # Sample data generator
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI
├── docker-compose.yml
├── .env.example
└── README.md
```

## Changing LLM Providers

The system supports multiple LLM providers via PydanticAI. To switch providers:

1. Update `LLM_MODEL` in `.env`:

```env
# OpenAI (default)
LLM_MODEL=openai:gpt-4o
OPENAI_API_KEY=sk-...

# Anthropic Claude
LLM_MODEL=anthropic:claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini
LLM_MODEL=gemini-1.5-pro
GEMINI_API_KEY=...
```

2. Restart services:
```bash
docker compose down
docker compose up --build
```

No code changes required - PydanticAI handles provider switching automatically.

## AI Agent Behavior

The AI agent is configured with a strict system prompt (backend/app/ai_agent.py:9) that enforces:

- **Sentiment**: positive, neutral, or negative
- **Urgency levels**:
  - `high`: Threatens cancellation, blocks paid service, or causes financial loss
  - `medium`: Functional issues without immediate impact
  - `low`: Feature requests, praise, or informational queries
- **Category**: Short phrase like "billing", "technical", "product", "account", "shipping"
- **Summary**: One concise sentence
- **Recommended Action**: Brief action for support team

### Retry Logic

If the AI returns invalid JSON or fails validation:
1. Automatically retries up to 2 times (configurable via prompt_config.json in Phase 2)
2. On persistent failure, stores the record with `analysis=null` and `analysis_error` field
3. All attempts are logged with request IDs for debugging
4. Phase 2: `agent_success` field tracks whether AI analysis succeeded

## Phase 2 Configuration

### Dynamic Prompt Tuning

Edit `backend/app/config/prompt_config.json` to customize AI behavior without code changes:

```json
{
  "bias_words": ["refund", "urgent", "asap", "broken"],
  "urgency_rules": {
    "high_indicators": ["can't access", "losing money"],
    "low_indicators": ["suggestion", "would be nice"]
  },
  "max_retries": 2,
  "version": "1.0"
}
```

Changes take effect on next container restart.

### Slack Integration

Get a Slack webhook URL from https://api.slack.com/messaging/webhooks and add to `.env`:

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

Triggers:
- **High-urgency feedback**: Instant alert with customer details and recommended action
- **Weekly summary**: Performance report with accuracy metrics and urgency breakdown

### Weekly Job Schedule

Configure the cron expression in `.env`:

```env
# Every Monday at 9 AM UTC (default)
SCHEDULE_CRON_WEEKLY=0 9 * * 1

# Every Friday at 6 PM UTC
# SCHEDULE_CRON_WEEKLY=0 18 * * 5

# First day of every month at midnight
# SCHEDULE_CRON_WEEKLY=0 0 1 * *
```

Reports are saved to `backend/reports/` directory.

### Human Override Workflow

1. Review feedback in dashboard
2. Identify AI mistakes (wrong sentiment, urgency, etc.)
3. Apply override via API:

```bash
curl -X POST http://localhost:8000/api/feedback/507f1f77bcf86cd799439011/override \
  -H "Content-Type: application/json" \
  -d '{
    "field": "urgency_level",
    "new_value": "high",
    "reason": "Customer mentioned critical business impact",
    "overridden_by": "jane.doe@company.com"
  }'
```

4. Override is recorded in audit trail
5. Metrics API reflects updated accuracy (1 - overrides/processed)

## Deployment

### Local Production Build

```bash
docker compose -f docker-compose.yml up --build -d
```

### Environment Variables for Production

Required:
- `MONGODB_URI`: MongoDB connection string
- `LLM_MODEL`: AI model identifier
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY`: At least one API key

Optional:
- `FASTAPI_PORT`: Backend port (default: 8000)
- `FRONTEND_PORT`: Frontend port (default: 5173)

Phase 2 Optional:
- `SLACK_WEBHOOK_URL`: Slack webhook for alerts and weekly summaries
- `SCHEDULE_CRON_WEEKLY`: Cron expression for weekly job (default: `0 9 * * 1`)

### Scaling Considerations

For production at scale:

1. **Add background task queue**: Replace synchronous AI calls with Celery/RQ
2. **Add Redis**: For WebSocket message broker and caching
3. **Rate limiting**: Implement per-user rate limits on feedback submission
4. **MongoDB replica set**: For high availability
5. **Load balancer**: Distribute traffic across multiple backend instances
6. **CDN**: Serve frontend static assets via CDN

## Monitoring & Logging

All API requests and AI calls are logged with structured logging:

```python
# View logs
docker compose logs -f backend
```

Log format includes:
- Timestamp
- Request ID (for tracing)
- Masked email addresses (privacy)
- AI analysis results
- Error details with stack traces

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push:

1. Backend linting (ruff, black)
2. Backend tests (pytest)
3. Frontend linting (eslint)
4. Frontend tests (vitest)
5. Frontend build
6. Docker image builds

To enable:
1. Push to GitHub
2. Add `OPENAI_API_KEY` to repository secrets (Settings → Secrets)
3. Workflow runs automatically on push/PR

## Troubleshooting

### "MongoDB connection failed"

Ensure MongoDB container is running:
```bash
docker compose ps
docker compose up mongodb
```

### "AI validation failed after 3 attempts"

- Check your API key is valid and has credits
- Verify `LLM_MODEL` format matches provider syntax
- Check backend logs: `docker compose logs backend`

### WebSocket not connecting

- Ensure backend is running on port 8000
- Check `VITE_WS_URL` in `.env` matches your setup
- For production, use `wss://` protocol with HTTPS

### Port already in use

Change ports in `.env`:
```env
FASTAPI_PORT=8001
FRONTEND_PORT=5174
```

Update docker-compose.yml port mappings accordingly.

## License

MIT License - see LICENSE file for details

## Support

For issues, please check:
1. Docker containers are running: `docker compose ps`
2. Logs for errors: `docker compose logs`
3. API health: http://localhost:8000/health
4. Environment variables are set correctly

---

**Built with**: FastAPI, React, PydanticAI, MongoDB, Docker, TypeScript, Tailwind CSS
