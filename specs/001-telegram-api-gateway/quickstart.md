# Quickstart: RelayStack API

## Prerequisites

- Docker & Docker Compose (recommended)
- Python 3.12 (for local development)
- Telegram account with a working phone number

## Local Development

```bash
# Clone and enter the repo
git clone <repo-url> && cd relaystack-api

# Create virtual environment
python3.12 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment config
cp .env.example .env
# Edit .env: set DATABASE_URL, REDIS_URL, API_KEYS

# Start dependencies (PostgreSQL + Redis)
docker compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start the app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Compose (full stack)

```bash
docker compose up --build
```

Services:
- `app` — FastAPI gateway on port 8000
- `postgres` — PostgreSQL on port 5432
- `redis` — Redis on port 6379

## Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# Create an instance
curl -X POST http://localhost:8000/instances \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Account"}'

# Open API docs
open http://localhost:8000/docs
```

## Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing

# Specific test file
pytest tests/test_encryption.py -v
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | `postgresql+asyncpg://user:pass@localhost:5432/telegram_gateway` | PostgreSQL connection string |
| REDIS_URL | `redis://localhost:6379/0` | Redis connection string |
| API_KEYS | (none) | Comma-separated list of API keys for initial setup |
| ENCRYPTION_KEY | (auto-generated) | AES-256 key for session encryption |
| WEBHOOK_RETRY_MAX | 3 | Max webhook delivery attempts |
| WEBHOOK_RETRY_BASE_DELAY | 60 | Base delay in seconds for exponential backoff |

## Project Layout

```
app/                    # Application source
  main.py               # FastAPI app entrypoint
  config.py             # Environment config
  security/             # API keys, encryption, webhook signing
  db/                   # Database models, session, repositories
  schemas/              # Pydantic request/response models
  api/                  # Route handlers
  services/             # Business logic (auth, messaging, webhooks)
  workers/              # Background workers (webhook retries)
tests/                  # Test suite
migrations/             # Alembic migrations
```
