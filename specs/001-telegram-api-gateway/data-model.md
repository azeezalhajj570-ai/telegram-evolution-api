# Data Model: Telegram API Gateway

**Entities, fields, relationships, and state transitions.**

---

## Entity: `api_key`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| key_hash | str(128) | NOT NULL, UNIQUE | bcrypt hash of the API key token |
| name | str(128) | NOT NULL | Human-readable label for the key |
| is_active | bool | NOT NULL, default=true | Whether the key can authenticate |
| created_at | datetime | NOT NULL, auto | Timestamp of creation |

**Relationships**: none (standalone table for MVP; user model is out of scope)

---

## Entity: `instance`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| name | str(256) | NOT NULL | Human-readable name |
| phone_number | str(32) | NULLABLE | Phone number in international format |
| status | enum | NOT NULL, default=pending | See state machine below |
| session_encrypted | text | NULLABLE | AES-256-GCM encrypted Telethon StringSession |
| phone_code_hash | str(64) | NULLABLE | Hash returned by Telegram during login (for OTP verification) |
| twofa_password_hash | str(128) | NULLABLE | Argon2/blake2b hash of 2FA password (for reconnection) |
| created_at | datetime | NOT NULL, auto | Timestamp of creation |
| updated_at | datetime | NOT NULL, auto | Timestamp of last update |

**State Machine**:

```text
                   ┌──────────┐
                   │  PENDING │ (initial state on creation)
                   └────┬─────┘
                        │ send_code()
                        ▼
               ┌────────────────┐
               │ CODE_SENT      │ (OTP sent to phone)
               └───────┬────────┘
                       │ verify_code()
                  ┌────┴────┐
                  ▼         ▼
          ┌──────────┐  ┌──────────┐  (wrong OTP → back to CODE_SENT)
          │ AUTH_REQ_ │  │  PENDING │
          │   2FA     │  └──────────┘
          └────┬─────┘
               │ submit_2fa()
               ▼
        ┌──────────────┐
        │ AUTHENTICATED │ (Telegram session acquired)
        └──────┬───────┘
               │ connect()
               ▼
        ┌──────────────┐
        │  CONNECTED   │ (Telethon client running, receiving events)
        └──────┬───────┘
               │ disconnect()        │ session invalidated
               ▼                     ▼
        ┌──────────────┐    ┌──────────────┐
        │DISCONNECTED  │    │ AUTH_REQUIRED│
        └──────────────┘    └──────────────┘
               │                    │
               └── connect() ───────┘
                        │
                        ▼
                  ┌──────────────┐
                  │    ERROR     │ (any step fails unrecoverably)
                  └──────────────┘
```

**Validation Rules**:
- `phone_number` must be set before `send_code()` can be called
- `session_encrypted` is only written after successful OTP (+ optional 2FA) verification
- DELETE cascades to webhook and webhook_delivery rows

---

## Entity: `webhook`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| instance_id | UUID | FK → instance.id, UNIQUE, NOT NULL | One webhook per instance |
| url | str(2048) | NOT NULL | Target URL for webhook delivery |
| secret | str(64) | NOT NULL | Random secret for HMAC SHA256 signing |
| is_active | bool | NOT NULL, default=true | Whether webhook delivery is enabled |
| max_retries | int | NOT NULL, default=3 | Maximum delivery attempts |
| created_at | datetime | NOT NULL, auto | Timestamp of creation |
| updated_at | datetime | NOT NULL, auto | Timestamp of last update |

**Relationships**:
- Belongs to `instance` (1:1 — each instance has at most one webhook)  
- Has many `webhook_delivery` records

---

## Entity: `webhook_delivery`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| webhook_id | UUID | FK → webhook.id, NOT NULL | Parent webhook config |
| event_type | str(64) | NOT NULL | e.g. "message", "message_edited" |
| payload | jsonb | NOT NULL | Serialized event payload |
| status | enum | NOT NULL, default=pending | pending, delivered, failed |
| attempt_count | int | NOT NULL, default=0 | Number of delivery attempts |
| last_status_code | int | NULLABLE | HTTP status from last attempt |
| last_attempt_at | datetime | NULLABLE | Timestamp of last attempt |
| created_at | datetime | NOT NULL, auto | Timestamp of creation |

**Relationships**:
- Belongs to `webhook`

---

## Entity: `auth_state` (transient)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| instance_id | UUID | FK → instance.id, PK | One auth state per instance |
| flow_status | enum | NOT NULL | idle, code_sent, awaiting_2fa |
| phone_code_hash | str(64) | NULLABLE | Telegram's code hash for OTP verification |
| phone_number | str(32) | NULLABLE | Phone number used in current flow |
| created_at | datetime | NOT NULL, auto | Timestamp of creation |
| expires_at | datetime | NOT NULL | TTL after which flow resets |

**Notes**:
- Stored in PostgreSQL alongside instance data
- One row per instance that has an active auth flow
- `expires_at` auto-resets expired flows (TTL = 5 minutes)

---

## Entity Relationships Diagram

```text
api_key (standalone — used for endpoint auth)
    │
    │ (no FK — key is validated, not tied to instance ownership in MVP)
    │
instance ──1:1──→ webhook ──1:N──→ webhook_delivery
    │
    └──1:1──→ auth_state (transient, TTL-based)
```

## Indexing Strategy

| Table | Index | Type | Rationale |
|-------|-------|------|-----------|
| instance | status | B-tree | Filter connected instances on startup |
| instance | phone_number | UNIQUE B-tree | Prevent duplicate phone registration |
| webhook | instance_id | UNIQUE B-tree | FK lookup + 1:1 enforcement |
| webhook_delivery | webhook_id, status | Composite B-tree | Find pending deliveries for retry worker |
| api_key | key_hash | UNIQUE B-tree | API key lookup |
