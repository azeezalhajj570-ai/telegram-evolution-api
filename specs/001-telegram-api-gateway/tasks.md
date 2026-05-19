---
description: "Implementation tasks for RelayStack API feature"
---

# Tasks: RelayStack API

**Input**: Design documents from `/specs/001-telegram-api-gateway/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are MANDATORY per the project constitution — every feature MUST include contract, integration, and unit tests where applicable. Tests MUST be written before implementation code (red-green-refactor).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- `app/` at repository root for source code
- `tests/` at repository root for test suite
- `migrations/` at repository root for Alembic
- Dockerfile and docker-compose.yml at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize FastAPI project — create `pyproject.toml` with dependencies (fastapi, uvicorn, telethon, sqlalchemy[asyncio], alembic, psycopg2-binary, asyncpg, pydantic-settings, pydantic, httpx, redis), directory structure (`app/`, `tests/`, `migrations/`, `Dockerfile`, `docker-compose.yml`), and stub `app/main.py` with basic FastAPI app
- [ ] T002 [P] Add settings management — implement `app/config.py` using `pydantic-settings` with `Settings` class for `DATABASE_URL`, `REDIS_URL`, `ENCRYPTION_KEY`, `API_KEYS`, `WEBHOOK_RETRY_MAX`, `WEBHOOK_RETRY_BASE_DELAY`, loading from environment variables with `.env` file support
- [ ] T003 [P] Add Dockerfile and `docker-compose.yml` — create multi-stage `Dockerfile` for the FastAPI app with uvicorn, and `docker-compose.yml` with `app`, `postgres:16`, and `redis:7` services, env vars, ports (8000, 5432, 6379), and volume mounts for PostgreSQL data

**Checkpoint**: Project skeleton runs — `docker compose up` starts all three services without errors

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Add async SQLAlchemy database setup — implement `app/db/database.py` with `create_async_engine`, `async_sessionmaker`, `AsyncSession` factory, `Base` declarative base, and `get_db` async dependency. Configure engine from `config.py` settings
- [ ] T005 [P] Implement encryption service — implement `app/security/encryption.py` with AES-256-GCM encrypt/decrypt functions using `cryptography` library. `encrypt(plaintext: str, key: bytes) -> str` returns base64-encoded ciphertext with nonce prepended. `decrypt(ciphertext_b64: str, key: bytes) -> str` reverses. Include unit test
- [ ] T006 Create Alembic migrations setup — run `alembic init migrations`, configure `migrations/env.py` to use async SQLAlchemy engine from `app/db/database.py`, set `target_metadata = Base.metadata`, generate initial migration revision
- [ ] T007 Implement API key model and hashing — add `ApiKey` model to `app/db/models.py` (id UUID, key_hash string, name string, is_active bool, created_at datetime). Implement `app/security/api_keys.py` with `hash_api_key(plaintext: str) -> str` (bcrypt), `verify_api_key(plaintext: str, key_hash: str) -> bool`, and `generate_api_key() -> str` that returns a random token
- [ ] T008 Implement API key authentication dependency — implement `app/security/api_keys.py` `verify_api_key_dependency` as a FastAPI `Depends` callable that reads `X-API-Key` header, hashes it, looks up in DB via `ApiKey` model, and returns the key or raises HTTP 401. Add `require_api_key` reusable dependency
- [ ] T009 Implement instance database model — add `Instance` model to `app/db/models.py` with fields from data-model.md (id UUID, name string, phone_number nullable, status enum/string with default "pending", session_encrypted nullable text, phone_code_hash nullable string, twofa_password_hash nullable string, created_at, updated_at). Add status choices: pending, code_sent, awaiting_2fa, authenticated, connected, disconnected, auth_required, error
- [ ] T010 Implement webhook database model — add `Webhook` model to `app/db/models.py` with fields (id UUID, instance_id FK with unique constraint, url string, secret string, is_active bool default true, max_retries int default 3, created_at, updated_at). Add relationship to Instance
- [ ] T011 Implement webhook delivery database model — add `WebhookDelivery` model to `app/db/models.py` with fields (id UUID, webhook_id FK, event_type string, payload JSONB, status string default "pending", attempt_count int default 0, last_status_code int nullable, last_attempt_at datetime nullable, created_at datetime). Add relationship to Webhook
- [ ] T012 [P] Implement `app/db/repositories.py` — create async repository classes: `ApiKeyRepository` (get_by_hash), `InstanceRepository` (create, get, get_all, update, delete, get_by_status), `WebhookRepository` (create, get_by_instance, delete), `WebhookDeliveryRepository` (create, get_pending, mark_delivered, mark_failed). Each method accepts `AsyncSession` and returns the model or result

**Checkpoint**: Database models defined, migrations runnable, repositories functional — foundation ready for all user stories

---

## Phase 3: User Story 1 - Instance Creation and Authentication (Priority: P1) 🎯 MVP

**Goal**: Create Telegram account instances and complete the full authentication flow (send-code → verify-otp → 2fa → connect → disconnect)

**Independent Test**: Create instance → request login code → submit OTP → (2FA if needed) → connect → verify status "connected" → disconnect → verify status "disconnected". All via API calls with mocked Telethon

### Tests for User Story 1 (MANDATORY) ⚠️

- [ ] T013 [P] [US1] Contract test for instance CRUD endpoints in `tests/test_instances.py` — test create, list, get, delete via test client with valid and invalid API keys
- [ ] T014 [P] [US1] Contract test for auth flow endpoints in `tests/test_auth.py` — test send-code, verify-code, 2fa, connect, disconnect, status. Mock Telethon client to avoid real network calls
- [ ] T015 [P] [US1] Unit test for encryption service in `tests/test_encryption.py` — test encrypt/decrypt round-trip, decrypt with wrong key, decrypt with tampered ciphertext

### Implementation for User Story 1

- [ ] T016 [P] [US1] Implement instance Pydantic schemas in `app/schemas/instances.py` — `InstanceCreate` (name), `InstanceResponse` (all fields), `InstanceListResponse` (list of InstanceResponse). Include validation (name 1-256 chars)
- [ ] T017 [P] [US1] Implement auth flow Pydantic schemas in `app/schemas/auth.py` — `SendCodeRequest` (phone_number with regex validation), `VerifyCodeRequest` (code string), `TwoFARequest` (password string), `AuthStatusResponse` (status, twofa_required bool)
- [ ] T018 [US1] Implement instance CRUD API endpoints in `app/api/instances.py` — `POST /instances` (create), `GET /instances` (list), `GET /instances/{id}` (get), `DELETE /instances/{id}` (delete, disconnects first). All protected by `require_api_key` dependency
- [ ] T019 [P] [US1] Implement TelegramClientManager in `app/services/telegram_manager.py` — singleton class managing a `dict[str, TelegramClient]` keyed by instance ID. Methods: `start_client(instance_id, session_str, api_id, api_hash)`, `get_client(instance_id) -> TelegramClient`, `stop_client(instance_id)`, `stop_all()`, `get_connected_ids() -> list[str]`. Thread-safe with asyncio lock
- [ ] T020 [US1] Implement Telethon client factory in `app/services/telegram_manager.py` — `_create_client(session_str, api_id, api_hash)` that creates `TelegramClient(StringSession(session_str), api_id, api_hash)` with appropriate timeout and flood-wait settings. Load `api_id` and `api_hash` from `config.py` (Telegram API credentials from my.telegram.org)
- [ ] T021 [P] [US1] Implement auth Pydantic schemas for status — add `InstanceStatusResponse` to `app/schemas/instances.py` with all instance fields plus `has_webhook` bool
- [ ] T022 [US1] Implement auth service in `app/services/telegram_auth.py` — `send_code(instance_id, phone_number)` creates temp Telethon client, calls `SendCodeRequest`, stores `phone_code_hash` in DB, sets status to "code_sent". `verify_code(instance_id, code)` calls `SignInRequest` with stored hash, handles `SessionPasswordNeededError` by setting status to "awaiting_2fa", otherwise saves encrypted session via `encrypt()` and sets "authenticated". `submit_2fa(instance_id, password)` calls `SignInRequest` with password, saves encrypted session
- [ ] T023 [US1] Save encrypted StringSession — after successful login in `verify_code()` or `submit_2fa()`, serialize the Telethon client's session via `client.session.save()`, encrypt with `encryption.encrypt()`, store in `instance.session_encrypted` via repository. Clear `phone_code_hash` on completion
- [ ] T024 [US1] Implement auth API endpoints in `app/api/auth.py` — `POST /instances/{id}/auth/send-code`, `POST /instances/{id}/auth/verify-code`, `POST /instances/{id}/auth/2fa`. Each validates instance exists, checks current status, calls auth service, returns appropriate response
- [ ] T025 [US1] Implement `/instances/{id}/auth/connect` — loads encrypted session from DB, decrypts, creates Telethon client via `TelegramClientManager.start_client()`, starts client, sets status to "connected". Returns `{"status": "connected"}`
- [ ] T026 [US1] Implement `/instances/{id}/auth/disconnect` — gets client from `TelegramClientManager`, disconnects, calls `TelegramClientManager.stop_client()`, sets status to "disconnected" but preserves encrypted session in DB
- [ ] T027 [US1] Implement `/instances/{id}/status` — returns full `InstanceStatusResponse` with current status, whether it has a session, and whether a webhook is configured
- [ ] T028 [US1] Add startup routine in `app/main.py` lifespan — on startup, query all instances with status="connected", load session, decrypt, start Telethon client via `TelegramClientManager`. On failure with session error, set status to "auth_required"
- [ ] T029 [US1] Add graceful shutdown in `app/main.py` lifespan — on shutdown, call `TelegramClientManager.stop_all()` to disconnect all clients gracefully with timeout per client

**Checkpoint**: Full auth flow works — create → send-code → verify-otp → 2fa → connect → disconnect → reconnect on restart. MVP complete

---

## Phase 4: User Story 2 - Sending Messages via API (Priority: P1)

**Goal**: Send text messages from a connected instance to any Telegram chat

**Independent Test**: Connect an instance → send text message to a known chat → verify message appears in destination. With mocked Telethon, verify correct API calls were made

### Tests for User Story 2 (MANDATORY) ⚠️

- [ ] T030 [P] [US2] Contract test for send-message endpoint in `tests/test_messages.py` — test success, instance not connected, invalid chat, rate limit response

### Implementation for User Story 2

- [ ] T031 [P] [US2] Implement message Pydantic schemas in `app/schemas/messages.py` — `SendMessageRequest` (chat_id: int, text: str, with validation: text 1-4096 chars), `SendMessageResponse` (message_id: int, chat_id: int, status: str)
- [ ] T032 [US2] Implement messaging service in `app/services/messaging.py` — `send_message(instance_id, chat_id, text)` gets Telethon client from manager, calls `client.send_message(chat_id, text)`, returns message ID. Catch `FloodWaitError`, `RPCError` (chat invalid), `ValueError` (not connected)
- [ ] T033 [US2] Implement send-message API endpoint in `app/api/messages.py` — `POST /instances/{id}/send-message` validates instance is connected, calls messaging service, returns response
- [ ] T034 [US2] Add FloodWaitError handling in `app/services/rate_limits.py` — catch `FloodWaitError(seconds=X)`, return `HTTP 429` with `{"error": "rate_limited", "retry_after_seconds": X, "detail": "..."}`. Log warning without exposing the exception details

**Checkpoint**: Sending works — any connected instance can send messages and FloodWait is handled gracefully

---

## Phase 5: User Story 3 - Incoming Message Webhooks (Priority: P2)

**Goal**: Receive incoming Telegram messages as signed webhook payloads delivered to a configurable URL

**Independent Test**: Configure webhook URL → receive a message on the Telegram account → verify webhook POST was sent to the configured URL with correct HMAC signature. With mocked Telethon event, verify dispatcher logic

### Tests for User Story 3 (MANDATORY) ⚠️

- [ ] T035 [P] [US3] Contract test for webhook CRUD endpoints in `tests/test_webhooks.py` — test create, get, delete, test-webhook
- [ ] T036 [P] [US3] Unit test for webhook signing in `tests/test_webhook_signing.py` — test sign and verify with known secret and payload
- [ ] T037 [US3] Integration test for webhook dispatcher in `tests/test_webhook_dispatcher.py` — mock httpx, trigger dispatch with fake event, verify POST called with correct URL, headers, body, and signature

### Implementation for User Story 3

- [ ] T038 [P] [US3] Implement webhook Pydantic schemas in `app/schemas/webhooks.py` — `WebhookCreateRequest` (url: HttpUrl), `WebhookResponse` (id, url, is_active, max_retries, secret masked, created_at), `WebhookTestResponse` (status, status_code)
- [ ] T039 [P] [US3] Implement webhook signing in `app/security/webhook_signing.py` — `sign_payload(payload: bytes, secret: str) -> str` computes HMAC SHA256 hex digest. `verify_signature(payload: bytes, secret: str, signature: str) -> bool` for receiver-side verification
- [ ] T040 [US3] Implement webhook CRUD API endpoints in `app/api/webhooks.py` — `POST /instances/{id}/webhook` (creates webhook with random secret), `GET /instances/{id}/webhook`, `DELETE /instances/{id}/webhook`. One webhook per instance enforced by unique constraint
- [ ] T041 [US3] Implement webhook dispatcher in `app/services/webhook_dispatcher.py` — `dispatch(instance_id, event_type, event_data)` loads webhook config, builds payload, signs with HMAC, POSTs to URL via httpx.AsyncClient. Creates `WebhookDelivery` record. On 2xx: marks delivered. On error: queues retry
- [ ] T042 [US3] Add NewMessage event listener — in `TelegramClientManager.start_client()`, register `@client.on(events.NewMessage)` handler. Handler captures message data (message_id, chat_id, sender_id, text, date), calls `normalize_message()` to create normalized event, then calls `webhook_dispatcher.dispatch()`
- [ ] T043 [US3] Add message normalization in `app/services/webhook_dispatcher.py` — `normalize_message(event: events.NewMessage.Event) -> dict` extracts sender name from `event.sender.first_name`/`last_name`, chat title from `event.chat.title`, returns dict matching webhook event contract format
- [ ] T044 [P] [US3] Implement `POST /instances/{id}/webhook/test` — generates a fake test event, dispatches to the configured webhook URL, returns delivery status to caller
- [ ] T045 [US3] Implement basic webhook retry logic — `app/workers/webhook_worker.py` background task that queries `WebhookDelivery` records with status="pending" and attempt_count < max_retries, retries with exponential backoff (base delay × 2^attempt), updates delivery record

**Checkpoint**: Real-time webhook delivery works — incoming Telegram messages are normalized, signed, and delivered to the configured URL with retry on failure

---

## Phase 6: User Story 4 - Chat and Message Management (Priority: P3)

**Goal**: List Telegram chats and read recent messages from a connected instance

**Independent Test**: Connect an instance → list chats → verify known chats appear → get messages from a chat → verify messages returned. With mocked Telethon, verify correct API calls

### Tests for User Story 4 (MANDATORY) ⚠️

- [ ] T046 [P] [US4] Contract test for chats endpoints in `tests/test_chats.py` — test list chats, get messages, pagination, instance not connected

### Implementation for User Story 4

- [ ] T047 [P] [US4] Implement chat Pydantic schemas in `app/schemas/messages.py` — `ChatInfo` (chat_id, title, type, unread_count, last_message), `ChatListResponse` (chats list), `MessageInfo` (message_id, chat_id, sender_id, text, date, is_outgoing), `MessagesResponse` (messages list)
- [ ] T048 [P] [US4] Implement chat service in `app/services/chats.py` — `list_chats(instance_id)` calls `client.get_dialogs()`, maps to `ChatInfo` list. `get_messages(instance_id, chat_id, limit, offset_id)` calls `client.get_messages(chat_id, limit=limit, offset_id=offset_id)`, maps to `MessageInfo` list
- [ ] T049 [US4] Implement chats API endpoints in `app/api/chats.py` — `GET /instances/{id}/chats` and `GET /instances/{id}/chats/{chat_id}/messages` with query params (limit, offset_id). Both validate instance is connected

**Checkpoint**: Chat browsing works — developers can list chats and read messages from any connected instance

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T050 [P] Add pytest test suite configuration — create `tests/conftest.py` with fixtures: async test client (httpx.AsyncClient with app), test database (separate SQLite or test PostgreSQL), `override_get_db` dependency, mocked Telethon client fixture using `unittest.mock.AsyncMock`, sample instance fixture, sample webhook fixture
- [ ] T051 [P] Add README with setup and API examples — write `README.md` covering: what the project does, prerequisites (Python 3.12, Docker), quickstart (docker compose up), API overview with curl examples for each endpoint, environment variables table, project structure tree
- [ ] T052 [P] Add OpenAPI tags and descriptions — tag all routers in `app/api/*.py` with `tags=["Instances"]`, `tags=["Auth"]`, `tags=["Messages"]`, `tags=["Chats"]`, `tags=["Webhooks"]`. Add summary and description docstrings to each endpoint. Add `title="RelayStack API"` and `version="0.1.0"` to FastAPI app
- [ ] T053 [P] Add production notes — create `PRODUCTION.md` with: Telegram account safety guidelines (don't use primary account, monitor for bans, respect rate limits), rate limit handling behavior, scaling considerations (multiple app instances need shared session storage), monitoring recommendations, backup and restore of encrypted sessions, known limitations
- [ ] T054 Add overall error handling middleware — implement global exception handler in `app/main.py` that catches unhandled exceptions, logs with traceback (no sensitive data), returns `{"error": "internal_error", "detail": "An unexpected error occurred"}` with HTTP 500
- [ ] T055 Add health check endpoint — `GET /health` returns `{"status": "healthy", "db": "connected", "redis": "connected", "instances": {"total": N, "connected": N}}` with HTTP 503 if DB or Redis is unreachable

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 - Auth (Phase 3)**: Depends on Foundational — BLOCKS US2, US3, US4
- **US2 - Messages (Phase 4)**: Depends on US1 (needs connected instance)
- **US3 - Webhooks (Phase 5)**: Depends on US1 (needs Telethon client running, connected instance)
- **US4 - Chats (Phase 6)**: Depends on US1 (needs connected instance)
- **Polish (Phase 7)**: Depends on all desired user stories complete

### Within Each User Story

- Tests MUST be written and FAIL before implementation (mandatory per constitution)
- Schemas before services (define data contracts)
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 — No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 (needs connected instance and TelegramClientManager)
- **User Story 3 (P2)**: Depends on US1 (needs TelegramClientManager and connected instance)
- **User Story 4 (P3)**: Depends on US1 (needs connected instance)

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003)
- Phase 2: T005 (encryption) is [P] — no DB dependency
- Phase 3: T013, T014, T015 (tests) are [P]; T016, T017 (schemas) are [P]; T021 (status schema) is [P]
- Phase 3: T019 (TelegramClientManager) is [P] with T018 (CRUD endpoints) — different files, different concerns
- Phase 5: T038 (schemas) [P], T039 (signing) [P] can start together
- Phase 7: All tasks are [P] — different files, independent

### Parallel Example: User Story 1

```bash
# Launch tests and schemas together:
Task: "T013 [P] [US1] Contract test for instance CRUD endpoints"
Task: "T014 [P] [US1] Contract test for auth flow endpoints"
Task: "T015 [P] [US1] Unit test for encryption service"
Task: "T016 [P] [US1] Instance Pydantic schemas"
Task: "T017 [P] [US1] Auth flow Pydantic schemas"

# Once tests+schema done, launch implementation:
Task: "T018 [US1] Instance CRUD API endpoints"
Task: "T019 [P] [US1] TelegramClientManager"
```

### Parallel Example: User Story 2

```bash
# All at once:
Task: "T030 [P] [US2] Contract test for send-message"
Task: "T031 [P] [US2] Message Pydantic schemas"
# After schema:
Task: "T032 [US2] Messaging service"
Task: "T033 [US2] Send-message endpoint"
Task: "T034 [US2] FloodWaitError handling"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T012)
3. Complete Phase 3: User Story 1 (T013-T029)
4. **STOP and VALIDATE**: Auth flow fully functional via API
5. Deploy/demo if ready — 18 tasks total, ~25 files

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Auth flow working → **MVP!**
3. Add User Story 2 → Sending messages → Deploy/Demo
4. Add User Story 3 → Webhook delivery → Deploy/Demo
5. Add User Story 4 → Chat management → Deploy/Demo
6. Final Phase → Polish, tests, docs

### Parallel Team Strategy

With multiple developers:
1. Team completes Phase 1 + Phase 2 together (12 tasks)
2. Once Foundational is done:
   - Developer A: User Story 1 (auth flow)
   - Developer B: User Story 2 (messaging) — needs US1 for end-to-end test
   - Developer C: User Story 4 (chats) — needs US1 for end-to-end test
3. Developer D: User Story 3 (webhooks) — needs US1
4. Polish phase after all stories complete

---

## Notes

- 55 total tasks across 7 phases
- 4 user stories (2 P1, 1 P2, 1 P3)
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story independently completable and testable
- Verify tests fail before implementing (red-green-refactor)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
