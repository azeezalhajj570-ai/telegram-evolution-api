# Contract: Chats API

Base path: `/instances/{id}/chats`
All endpoints require `X-API-Key` header.

---

## List Chats

`GET /instances/{id}/chats`

**Response** `200`:
```json
{
  "chats": [
    {
      "chat_id": 123456789,
      "title": "My Group",
      "type": "group",
      "unread_count": 5,
      "last_message": {
        "text": "Hello!",
        "sender_id": 987654321,
        "date": "2026-05-16T10:00:00Z"
      }
    }
  ]
}
```

**Chat types**: `private`, `group`, `supergroup`, `channel`

**Errors**:
- `400` instance not connected
- `404` instance not found

---

## Get Chat Messages

`GET /instances/{id}/chats/{chat_id}/messages`

**Query parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | int | 50 | Max messages to return (1-100) |
| offset_id | int | null | Message ID to paginate from (exclusive) |

**Response** `200`:
```json
{
  "messages": [
    {
      "message_id": 42,
      "chat_id": 123456789,
      "sender_id": 987654321,
      "text": "Hello!",
      "date": "2026-05-16T10:00:00Z",
      "is_outgoing": false
    }
  ]
}
```

**Errors**:
- `400` instance not connected
- `404` instance not found / chat not found
