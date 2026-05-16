# Telegram API Gateway

Self-hosted REST API Gateway for Telegram accounts using Telethon and FastAPI. Manage multiple Telegram instances, send messages, receive webhooks, and browse chats — all through a simple HTTP API.

## Quickstart

```bash
docker compose up --build
```

Services start on:
- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

API docs: http://localhost:8000/docs

## Prerequisites

1. Telegram API credentials from https://my.telegram.org/apps
2. Docker & Docker Compose

## Configuration

Copy `.env.example` to `.env` and set:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `ENCRYPTION_KEY` | 32-byte key for session encryption |
| `API_KEYS` | Comma-separated API keys for authentication |
| `TELEGRAM_API_ID` | API ID from my.telegram.org |
| `TELEGRAM_API_HASH` | API hash from my.telegram.org |

## API Overview

All endpoints except `/health` require `Authorization: Bearer <api-key>` header.

### Instances

```bash
# Create
curl -X POST http://localhost:8000/instances \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Account"}'

# List
curl http://localhost:8000/instances \
  -H "Authorization: Bearer $API_KEY"
```

### Authentication

```bash
# Send login code
curl -X POST http://localhost:8000/instances/$ID/auth/send-code \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"phone_number": "+5511999999999"}'

# Verify code
curl -X POST http://localhost:8000/instances/$ID/auth/verify-code \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"code": "12345"}'

# Submit 2FA (if required)
curl -X POST http://localhost:8000/instances/$ID/auth/2fa \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"password": "my_2fa"}'

# Connect
curl -X POST http://localhost:8000/instances/$ID/auth/connect \
  -H "Authorization: Bearer $API_KEY"
```

### Messaging

```bash
curl -X POST http://localhost:8000/instances/$ID/send-message \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"chat_id": 123456789, "text": "Hello!"}'
```

### Webhooks

```bash
# Configure
curl -X POST http://localhost:8000/instances/$ID/webhook \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"url": "https://myapp.com/webhook"}'

# Test
curl -X POST http://localhost:8000/instances/$ID/webhook/test \
  -H "Authorization: Bearer $API_KEY"
```

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
docker compose up -d postgres redis
alembic upgrade head
uvicorn app.main:app --reload
pytest
```

## Project Layout

```
app/
  main.py              # FastAPI app entrypoint
  config.py            # Environment configuration
  security/            # API keys, encryption, webhook signing
  db/                  # Database models, session, repositories
  schemas/             # Pydantic request/response models
  api/                 # Route handlers
  services/            # Business logic
  workers/             # Background workers
tests/                 # Test suite
migrations/            # Alembic migrations
```
