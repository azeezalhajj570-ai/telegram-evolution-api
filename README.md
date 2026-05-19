# RelayStack API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Telethon](https://img.shields.io/badge/Telethon-1.37+-2596be.svg)](https://docs.telethon.dev/)

A self-hosted messaging automation API. Manage multiple Telegram accounts, send and receive messages, handle media, manage contacts/groups/channels, and receive real-time webhooks — all through a clean HTTP API. **Current provider: Telegram via [MTProto](https://core.telegram.org/mtproto).**

## Features

- **Multi-Account Management** — Create and manage multiple Telegram instances from a single gateway
- **Full Authentication Flow** — Phone code verification, 2FA support, automatic session persistence
- **Rich Messaging** — Send text, photos, documents, videos, audio, voice messages
- **Message Operations** — Reply, forward, edit, delete messages, add reactions
- **Contacts Management** — List, import, and delete contacts
- **Group Management** — Create groups, list groups, add/remove members
- **Channel Operations** — Join/leave channels, list channels, browse channel messages
- **Real-Time Webhooks** — Receive incoming messages via HTTP callbacks with HMAC signature verification
- **Async Message Queue** — Redis-backed queue with retry logic, dead-letter handling, and idempotency keys
- **Rate Limiting** — Per-instance rate limits with automatic FloodWait handling
- **Multi-Tenant SaaS** — Organizations, role-based access control, scoped API keys, usage tracking, audit logs
- **Observability** — Structured JSON logging, Prometheus metrics, health/readiness endpoints
- **Session Security** — Encrypted session storage, secure API key hashing

## Quick Start

### Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/azeezalhajj570-ai/relaystack-api.git
cd relaystack-api

# Configure environment
cp .env.example .env
# Edit .env with your Telegram API credentials

# Start all services
docker compose up --build
```

The API will be available at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

### Manual Setup

```bash
# Prerequisites: Python 3.9+, PostgreSQL, Redis

# Create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

## Configuration

Copy `.env.example` to `.env` and configure the following variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_API_ID` | Yes | API ID from [my.telegram.org](https://my.telegram.org/apps) |
| `TELEGRAM_API_HASH` | Yes | API hash from [my.telegram.org](https://my.telegram.org/apps) |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `ENCRYPTION_KEY` | Yes | 32-byte hex key for session encryption |
| `API_KEYS` | Yes | Comma-separated API keys for authentication |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |
| `RATE_LIMIT_MAX` | No | Max requests per window (default: `5`) |
| `RATE_LIMIT_WINDOW` | No | Rate limit window in seconds (default: `60`) |

### Generating an Encryption Key

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Generating API Keys

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## API Overview

All endpoints except `/health` require authentication via `Authorization: Bearer <api-key>` header.

### Instances

```bash
# Create a new instance
curl -X POST http://localhost:8000/instances \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Account"}'

# List all instances
curl http://localhost:8000/instances \
  -H "Authorization: Bearer $API_KEY"
```

### Authentication

```bash
# Send login code to phone number
curl -X POST http://localhost:8000/instances/$INSTANCE_ID/auth/send-code \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'

# Verify the received code
curl -X POST http://localhost:8000/instances/$INSTANCE_ID/auth/verify-code \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"code": "12345"}'

# Submit 2FA password (if required)
curl -X POST http://localhost:8000/instances/$INSTANCE_ID/auth/2fa \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"password": "my_2fa_password"}'

# Connect the instance
curl -X POST http://localhost:8000/instances/$INSTANCE_ID/auth/connect \
  -H "Authorization: Bearer $API_KEY"
```

### Messaging

```bash
# Send text message
curl -X POST http://localhost:8000/instances/$INSTANCE_ID/send-message \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 123456789, "text": "Hello from API!"}'

# Send photo
curl -X POST http://localhost:8000/instances/$INSTANCE_ID/send-message/photo \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 123456789, "file_path": "/path/to/photo.jpg", "caption": "Check this out"}'

# Reply to a message
curl -X POST http://localhost:8000/instances/$INSTANCE_ID/messages/reply \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 123456789, "reply_to_msg_id": 42, "text": "Replying!"}'

# Forward a message
curl -X POST http://localhost:8000/instances/$INSTANCE_ID/messages/forward \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"from_chat_id": 111, "to_chat_id": 222, "message_id": 42}'
```

### Webhooks

```bash
# Configure webhook URL
curl -X POST http://localhost:8000/instances/$INSTANCE_ID/webhook \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-app.com/webhook"}'

# Test webhook delivery
curl -X POST http://localhost:8000/instances/$INSTANCE_ID/webhook/test \
  -H "Authorization: Bearer $API_KEY"
```

### Organizations (Multi-Tenant)

```bash
# Create organization
curl -X POST http://localhost:8000/orgs \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Company"}'

# Create API key for organization
curl -X POST http://localhost:8000/orgs/$ORG_ID/api-keys \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "production-key", "scopes": ["instances:read", "instances:write", "messages:send"]}'
```

### Health & Metrics

```bash
# Health check
curl http://localhost:8000/health

# Prometheus metrics
curl http://localhost:8000/metrics
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│  API Layer                                                  │
│  ├── /instances   (CRUD)                                    │
│  ├── /auth        (send-code, verify, 2FA, connect)         │
│  ├── /messages    (send, reply, forward, edit, delete)      │
│  ├── /chats       (list, browse)                            │
│  ├── /webhooks    (configure, test)                         │
│  ├── /orgs        (organizations, members, keys, audit)     │
│  └── /metrics     (Prometheus)                              │
├─────────────────────────────────────────────────────────────┤
│  Services Layer                                             │
│  ├── TelegramClientManager  (connection pool)               │
│  ├── TelegramAuthService    (auth flow)                     │
│  ├── MessageQueueService    (Redis queue)                   │
│  ├── OrganizationService    (multi-tenant)                  │
│  └── EncryptionService      (session encryption)            │
├─────────────────────────────────────────────────────────────┤
│  Workers                                                    │
│  ├── Message Worker  (processes queued messages)            │
│  └── Webhook Worker  (retries failed deliveries)            │
└─────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│   PostgreSQL    │            │      Redis      │
│  (instances,    │            │  (queue, rate   │
│   orgs, keys)   │            │   limits, etc)  │
└─────────────────┘            └─────────────────┘
```

## Project Structure

```
├── app/
│   ├── api/                 # Route handlers
│   │   ├── instances.py
│   │   ├── auth.py
│   │   ├── messages.py
│   │   ├── chats.py
│   │   ├── webhooks.py
│   │   └── organizations.py
│   ├── db/                  # Database layer
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── database.py      # Connection setup
│   │   └── repositories.py  # Data access
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   │   ├── telegram_manager.py
│   │   ├── telegram_auth.py
│   │   ├── message_queue.py
│   │   └── organizations.py
│   ├── security/            # Auth & encryption
│   │   ├── api_keys.py
│   │   ├── encryption.py
│   │   └── webhook_signing.py
│   ├── workers/             # Background workers
│   │   ├── message_worker.py
│   │   └── webhook_worker.py
│   ├── config.py            # Environment config
│   └── main.py              # FastAPI entrypoint
├── tests/                   # Test suite
├── migrations/              # Alembic migrations
├── docker-compose.yml       # Docker setup
├── Dockerfile               # Container image
└── pyproject.toml           # Project metadata
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run linter
ruff check app tests

# Run type checker
mypy app
```

## Production Deployment

See [PRODUCTION.md](./PRODUCTION.md) for production notes including:
- Telegram account safety guidelines
- Rate limiting configuration
- Scaling recommendations
- Backup and recovery procedures
- Monitoring setup

## Security

- Session strings are encrypted at rest using Fernet symmetric encryption
- API keys are hashed with bcrypt before storage
- Webhook payloads are signed with HMAC-SHA256
- OTP codes, 2FA passwords, and session strings are never logged
- See [SECURITY.md](./SECURITY.md) for the full security policy

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on how to get started.

## License

This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Telegram. Use at your own risk. Be aware of Telegram's [Terms of Service](https://telegram.org/tos) and [API Documentation](https://core.telegram.org/api). Misuse of this tool may result in account restrictions or bans.
