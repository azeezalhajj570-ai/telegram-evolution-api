# Contract: Messages API

Base path: `/instances/{id}/send-message`
All endpoints require `X-API-Key` header.

---

## Send Message

`POST /instances/{id}/send-message`

**Request**:
```json
{
  "chat_id": 123456789,
  "text": "Hello from the gateway!"
}
```

**Response** `200`:
```json
{
  "message_id": 42,
  "chat_id": 123456789,
  "status": "delivered"
}
```

**Errors**:
- `400` instance not connected / chat not found
- `404` instance not found
- `429` rate limited — response includes `retry_after_seconds`:
  ```json
  {
    "error": "rate_limited",
    "retry_after_seconds": 30,
    "detail": "Telegram rate limit applied. Wait 30 seconds before retrying."
  }
  ```
