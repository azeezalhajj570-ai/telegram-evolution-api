# Research: Telegram API Gateway — Technology Decisions

**Phase 0 Output** — All decisions confirmed from user specification.

## Language & Runtime

| Decision | Rationale |
|----------|-----------|
| **Python 3.12** | User-specified. Telethon and FastAPI both fully support 3.12. Async-native ecosystem. |

## Core Dependencies

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| **FastAPI** | User-specified. Async-native, Pydantic v2 integration, OpenAPI auto-docs. | Flask (sync-only, no native async), Django REST (heavier) |
| **Telethon** | User-specified. Mature MTProto client with async support, event system, session management. | pyrogram (similar, MTProto v2), tdlib (C library, more complex build) |
| **SQLAlchemy 2.x async** | User-specified. Production-grade async ORM with Alembic migrations. | asyncpg raw SQL (no ORM), tortoise-orm (less mature) |
| **Alembic** | User-specified. Schema migration management for SQLAlchemy. | — |
| **Pydantic v2** | User-specified. Request/response validation, settings management. | — |
| **httpx** | User-specified. Async HTTP client for webhook delivery. | aiohttp, requests (sync-only) |
| **Redis** | User-specified. Webhook retry queue, rate-limit counters. | — |

## Storage

| Decision | Rationale |
|----------|-----------|
| **PostgreSQL** | User-specified. SQLAlchemy async support, JSONB for flexible payload storage. |
| **Redis** | User-specified. Low-latency queue/rate-limit operations. |

## Testing

| Decision | Rationale |
|----------|-----------|
| **pytest + pytest-asyncio** | User-specified. De facto standard for Python async testing. |
| **httpx (mock)** | User-specified. Mock webhook HTTP calls without network. |

## Deployment

| Decision | Rationale |
|----------|-----------|
| **Docker Compose** | User-specified. Services: app, postgres, redis. |

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **Client pool (TelegramClientManager)** | Singleton managing Telethon clients. Loads on startup, reuses clients across requests. Avoids per-request client creation overhead. |
| **AES-256-GCM session encryption** | Authenticated encryption with random nonce. Protects StringSession at rest. |
| **Redis queue for webhook retries** | Reliable retry with exponential backoff. Survives app restart. |
| **Instance-scoped rate limiting** | Redis sorted sets per instance. Prevents one aggressive instance from starving others. |
