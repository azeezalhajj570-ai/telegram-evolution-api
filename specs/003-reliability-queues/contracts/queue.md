# Contract: Queue & Jobs

All endpoints require `X-API-Key` header.

## Send Text (via queue)

`POST /instances/{id}/messages/send-text`

**Request**:
```json
{"chat_id": 123, "text": "Hello", "idempotency_key": "optional-client-key"}
```

**Response** `202`:
```json
{"job_id": "uuid", "status": "queued"}
```

## Send Media (via queue)

`POST /instances/{id}/messages/send-media`

Same response shape — returns job_id immediately, processing happens async.

## Get Job Status

`GET /instances/{id}/messages/jobs/{job_id}`

**Response** `200`:
```json
{
  "job_id": "uuid",
  "status": "delivered",
  "type": "send_text",
  "attempt_count": 1,
  "message_id": 42,
  "error": null,
  "created_at": "2026-05-16T12:00:00Z",
  "updated_at": "2026-05-16T12:00:05Z"
}
```

## Get Rate Limit Status

`GET /instances/{id}/rate-limit`

**Response** `200`:
```json
{
  "instance_id": "uuid",
  "remaining": 18,
  "limit": 20,
  "window_seconds": 60,
  "is_paused": false,
  "pause_remaining": 0,
  "reset_at": "2026-05-16T12:01:00Z"
}
```
