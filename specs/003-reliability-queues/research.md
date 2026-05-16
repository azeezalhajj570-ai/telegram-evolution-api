# Research: Reliability & Queues

## Queue Strategy

| Approach | Decision | Rationale |
|----------|----------|-----------|
| **Backend** | Redis lists (LPUSH/BRPOP) | Already have Redis; no additional deps; simple and proven |
| **Job format** | JSON string with job_id, type, payload, idempotency_key | Portable, easy to inspect |
| **Worker** | asyncio background task (in-process) | No separate container needed for MVP; same pattern as webhook worker |
| **Retry** | Exponential backoff: 60s, 120s, 240s; max 3 attempts | Standard retry pattern |
| **Dead-letter** | Separate Redis list `dead_letter:{instance_id}` | Survives restart via RDB |

## Job Status Tracking

Status stored in Redis hash `job:{job_id}` with fields: status, instance_id, type, payload, attempt_count, error, message_id, created_at, updated_at.

States: `queued → processing → delivered | failed → dead_letter`

## FloodWait Handling

When worker encounters FloodWaitError:
1. Store `flood_wait:{instance_id}` in Redis with TTL = retry_after seconds
2. Push job back to queue with delay
3. Worker skips instances with active flood_wait key

## Rate Limiting

| Level | Method | Limits |
|-------|--------|--------|
| Per-instance | Redis sorted set + sliding window | 20 msg / 60s (configurable) |
| Per-user (global) | Same approach, keyed by org scope | 100 msg / 60s (configurable) |
