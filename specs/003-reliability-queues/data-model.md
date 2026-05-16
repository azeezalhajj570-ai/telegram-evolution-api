# Data Model: Reliability & Queues

## Redis Keys

| Key Pattern | Type | TTL | Purpose |
|-------------|------|-----|---------|
| `queue:{instance_id}` | List | ∞ | FIFO send job queue per instance |
| `queue:dead_letter:{instance_id}` | List | 7d | Failed jobs past max retries |
| `job:{job_id}` | Hash | 7d | Job status + metadata |
| `flood_wait:{instance_id}` | String | dynamic | FloodWait pause (TTL = retry_after) |
| `ratelimit:instance:{instance_id}` | Sorted Set | 60s | Sliding window rate limit |
| `ratelimit:user:{user_id}` | Sorted Set | 60s | Global per-user rate limit |
| `idempotency:{key}` | String | 24h | Idempotency key dedup |

## Job Hash Fields

| Field | Type | Example |
|-------|------|---------|
| status | str | queued / processing / delivered / failed / dead_letter |
| instance_id | str | uuid |
| type | str | send_text / send_media |
| payload | str | JSON of original request |
| idempotency_key | str | client-provided key |
| attempt_count | int | 0 |
| max_retries | int | 3 |
| error | str | error message if failed |
| message_id | int | Telegram message ID if delivered |
| chat_id | int | target chat |
| created_at | float | timestamp |
| updated_at | float | timestamp |

## Rate Limit Response

```json
{
  "instance_id": "uuid",
  "remaining": 15,
  "limit": 20,
  "window_seconds": 60,
  "is_paused": false,
  "pause_remaining": 0,
  "reset_at": "2026-05-16T12:00:00Z"
}
```
