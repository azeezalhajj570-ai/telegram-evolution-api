# Contract: Webhook API

Base path: `/instances/{id}/webhook`
All endpoints require `X-API-Key` header.

---

## Configure Webhook

`POST /instances/{id}/webhook`

**Request**:
```json
{
  "url": "https://myapp.com/webhooks/telegram"
}
```

**Response** `201`:
```json
{
  "id": "uuid",
  "url": "https://myapp.com/webhooks/telegram",
  "is_active": true,
  "max_retries": 3,
  "created_at": "2026-05-16T00:00:00Z"
}
```

**Errors**:
- `400` instance not found / invalid URL
- `404` instance not found

---

## Get Webhook Config

`GET /instances/{id}/webhook`

**Response** `200`: Webhook object (same shape as create response)

**Response** `204`: No webhook configured (null body)

**Errors**: `404` instance not found

---

## Delete Webhook

`DELETE /instances/{id}/webhook`

**Response** `204`: No content

**Errors**: `404` instance not found

---

## Test Webhook

`POST /instances/{id}/webhook/test`

**Request**: (empty body)

**Response** `200`:
```json
{
  "status": "delivered",
  "status_code": 200
}
```

**Errors**:
- `400` no webhook configured / delivery failed
- `404` instance not found

---

## Webhook Event Payload

Sent as `POST` to the configured URL with header `X-Signature-256: <hex_hmac>`.

```json
{
  "event": "message",
  "instance_id": "uuid",
  "timestamp": "2026-05-16T10:00:00Z",
  "payload": {
    "message_id": 42,
    "chat_id": 123456789,
    "chat_title": "My Group",
    "sender_id": 987654321,
    "sender_name": "John Doe",
    "text": "Hello from Telegram!",
    "date": "2026-05-16T10:00:00Z"
  }
}
```

**Event types**: `message`, `message_edited`, `message_deleted`, `user_typing`

**Signature verification**: Compute HMAC SHA256 of the raw request body using the configured webhook `secret`. Compare against `X-Signature-256` header.
