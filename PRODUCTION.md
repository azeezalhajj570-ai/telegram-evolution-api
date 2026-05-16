# Production Notes: Telegram API Gateway

## Telegram Account Safety

- **Do not use your primary Telegram account.** Create a dedicated account for API use. Telegram may ban accounts that exhibit automated behavior.
- **Rate limits are enforced by Telegram.** The gateway handles `FloodWaitError` gracefully and reports `retry_after_seconds`. Your application must respect these delays.
- **Monitor account health.** Check instance statuses regularly. If an account enters `auth_required` status, the session was invalidated and re-authentication is needed.
- **Avoid rapid messaging.** Space out sends to natural human intervals. Sending too many messages too quickly triggers Telegram's anti-spam systems.
- **One session per account.** If you log in elsewhere (Telegram app, web, etc.), the gateway session will be invalidated.

## Rate Limiting

The gateway applies two layers of rate limiting:

1. **Telegram FloodWait**: Returned as `HTTP 429` with `retry_after_seconds`. These are non-negotiable — the gateway passes through Telegram's requirement.
2. **Application rate limit**: Per-instance rate limiting on the send-message endpoint (5 requests per 60 seconds by default). Configure via `RATE_LIMIT_MAX` and `RATE_LIMIT_WINDOW` environment variables.

## Scaling

- **Single server**: PostgreSQL + Redis on the same Docker network suffice for 5-20 instances.
- **Multiple app instances**: Sessions are stored in PostgreSQL (encrypted). All app instances share the same database. However, Telethon clients are in-memory — each app instance maintains its own client pool. Use a single app instance per gateway deployment.
- **Redis persistence**: Enable Redis persistence (RDB/AOF) to preserve rate-limit and webhook retry state across restarts.

## Monitoring

- **Health endpoint**: `GET /health` returns DB/Redis connectivity and instance counts.
- **Logs**: Structured JSON logging recommended. Set `LOG_LEVEL=INFO` for production.
- **Metrics**: Expose via `GET /metrics` (requires prometheus_client instrumentation).

## Backup and Restore

- **Database**: Regular PostgreSQL backups using `pg_dump`. Encrypted sessions are stored in the `instances` table.
- **Encryption key**: The `ENCRYPTION_KEY` environment variable is required to decrypt sessions. Losing it means all sessions are unrecoverable.
- **Recovery flow**: Restore DB → ensure same `ENCRYPTION_KEY` → restart gateway → instances reconnect automatically.

## Known Limitations (MVP)

- Single-user API key model (no per-user instance ownership)
- No message history storage — messages are delivered via webhook in real-time only
- No admin UI — configuration is API-only
- No Kubernetes/container orchestration support
- No analytics or usage metrics
