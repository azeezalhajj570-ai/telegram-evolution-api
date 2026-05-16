# Implementation Plan: Telegram API Gateway

**Branch**: `001-telegram-api-gateway` | **Date**: 2026-05-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-telegram-api-gateway/spec.md`

## Summary

Self-hosted REST API Gateway that manages Telegram account instances via Telethon. Provides instance lifecycle (create/auth/connect/disconnect/delete), message sending, chat listing, and real-time webhook delivery for incoming messages. Exposes a FastAPI HTTP interface authenticated by API keys.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Telethon, SQLAlchemy 2.x (async), Alembic, Pydantic v2, httpx, Redis (via redis-py)

**Storage**: PostgreSQL (primary data), Redis (webhook retry queue, rate-limit counters)

**Testing**: pytest, pytest-asyncio, httpx (mock for webhook tests)

**Target Platform**: Linux (Docker Compose deployment)

**Project Type**: web-service (REST API)

**Performance Goals**: <10s message delivery (SC-003), <15s webhook delivery (SC-004), 5+ concurrent instances (SC-005)

**Constraints**: <200ms p95 API response (excluding Telegram network calls), encrypted session storage, no sensitive data in logs

**Scale/Scope**: Single-server MVP, 5-20 Telegram instances, single PostgreSQL + single Redis

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Code Quality** ✅
- Pydantic v2 schemas for all request/response validation → typed, validated
- SQLAlchemy 2.x async ORM with type-annotated models
- FastAPI auto-generates OpenAPI spec → documentation follows
- Structured error responses with context (actionable error messages)

**II. Testing Standards** ✅
- Unit tests: encryption, API key hashing, webhook signing, Pydantic validation
- Integration tests: mocked Telethon client for auth + messaging flows
- Webhook dispatcher tests: httpx mock
- Red-green-refactor: write failing test first for each bug fix

**III. User Experience Consistency** ✅
- RESTful JSON API with consistent error schema
- All instance operations under `/instances/{id}` prefix
- Standard HTTP status codes (200, 201, 400, 401, 404, 429, 500)
- OpenAPI documentation via `/docs`

**IV. Performance Requirements** ✅
- Instance-scoped client pool (no per-request Telethon client creation)
- Async I/O throughout (FastAPI async + SQLAlchemy async + Telethon async)
- Redis-backed rate limiting per instance on send-message
- N+1 prevention: eager-load webhook config with instance query

**V. Security & Observability** ✅
- API key authentication on all endpoints (bcrypt-hashed keys in DB)
- AES-256-GCM encryption for Telethon StringSession
- HMAC SHA256 webhook payload signing
- Structured logging (no OTP/2FA/API key/session data in logs)
- Health endpoint (`GET /health`) exposing readiness + liveness

**GATE RESULT**: PASS ✅ — No violations. All principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-telegram-api-gateway/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 — technology decisions
├── data-model.md        # Phase 1 — entities, fields, relationships
├── quickstart.md        # Phase 1 — setup & run guide
├── contracts/           # Phase 1 — REST API contracts
│   ├── instances.md
│   ├── auth.md
│   ├── messages.md
│   ├── chats.md
│   ├── webhooks.md
│   └── health.md
└── tasks.md             # Phase 2 — NOT created by /speckit.plan
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── main.py                   # FastAPI app, lifespan, startup/shutdown
├── config.py                 # Settings via pydantic-settings
├── security/
│   ├── __init__.py
│   ├── api_keys.py           # API key hashing + verification
│   ├── encryption.py         # AES-256-GCM session encrypt/decrypt
│   └── webhook_signing.py    # HMAC SHA256 payload signing
├── db/
│   ├── __init__.py
│   ├── database.py           # AsyncSession factory, engine
│   ├── models.py             # SQLAlchemy ORM models
│   └── repositories.py       # DB access layer (CRUD)
├── schemas/
│   ├── __init__.py
│   ├── instances.py          # Instance CRUD request/response
│   ├── auth.py               # Auth flow request/response
│   ├── messages.py           # Message send/read request/response
│   └── webhooks.py           # Webhook config request/response
├── api/
│   ├── __init__.py
│   ├── instances.py          # GET/POST/DELETE /instances
│   ├── auth.py               # POST /instances/{id}/auth/*
│   ├── messages.py           # POST /instances/{id}/send-message
│   ├── chats.py              # GET /instances/{id}/chats
│   └── webhooks.py           # CRUD /instances/{id}/webhook
├── services/
│   ├── __init__.py
│   ├── telegram_manager.py   # Telethon client pool lifecycle
│   ├── telegram_auth.py      # Auth state machine (send_code → verify → 2fa → connect)
│   ├── messaging.py          # Send message via Telethon client
│   ├── chats.py              # List chats, get messages
│   ├── webhook_dispatcher.py # Normalize event → POST to webhook URL
│   └── rate_limits.py        # Redis-based per-instance rate limiting
└── workers/
    ├── __init__.py
    └── webhook_worker.py     # Process webhook retry queue from Redis

tests/
├── __init__.py
├── conftest.py               # Fixtures: async client, test DB, mocked Telethon
├── test_encryption.py        # Unit: encrypt/decrypt round-trip
├── test_api_keys.py           # Unit: hash + verify
├── test_webhook_signing.py   # Unit: HMAC SHA256 sign + verify
├── test_validation.py        # Unit: Pydantic schema validation
├── test_auth_flow.py         # Integration: mocked Telethon auth
├── test_messaging.py         # Integration: mocked Telethon send
└── test_webhook_dispatcher.py# Unit/Integration: httpx mock

migrations/
├── env.py
├── alembic.ini
└── versions/
    └── 001_initial_schema.py

Dockerfile
docker-compose.yml
pyproject.toml
README.md
```

**Structure Decision**: Single project layout (`app/`) with layered architecture (api → services → db/telethon). This is a pure backend web service — no frontend, no mobile. Tests mirror the app structure under `tests/`.

## Complexity Tracking

No Constitution violations found. No complexity justification required.

## Phase 0 — Research

**Purpose**: Confirm all technology decisions and resolve any unknowns before design.

**Findings documented in**: `research.md`

**No unknowns to resolve** — the user has explicitly specified all technology choices (Python 3.12, FastAPI, Telethon, PostgreSQL, SQLAlchemy 2.x async, Alembic, Redis, Pydantic v2, httpx, Docker Compose, pytest) and the architecture.

## Phase 1 — Design & Contracts

**Prerequisites**: research.md complete.

**Generated artifacts**:
1. `data-model.md` — Entity definitions, fields, relationships, state transitions
2. `contracts/` — REST API endpoint contracts (paths, methods, request/response shapes)
3. `quickstart.md` — Local dev setup, run, test instructions
4. `AGENTS.md` — Agent context update (plan reference between SPECKIT markers)
