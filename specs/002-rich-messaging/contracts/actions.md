# Contract: Message Actions

All endpoints require `X-API-Key` header. All use `application/json`.

## Reply

`POST /instances/{id}/messages/reply`

**Request**:
```json
{"chat_id": 123, "text": "Reply text", "reply_to": 42}
```

**Response** `200`:
```json
{"message_id": 43, "status": "delivered"}
```

## Forward

`POST /instances/{id}/messages/forward`

**Request**:
```json
{"from_chat_id": 123, "message_id": 42, "to_chat_id": 456}
```

**Response** `200`:
```json
{"message_id": 44, "status": "delivered"}
```

## Edit

`PATCH /instances/{id}/messages/{message_id}`

**Request**:
```json
{"text": "Updated text"}
```

**Response** `200`:
```json
{"message_id": 42, "status": "edited"}
```

## Delete

`DELETE /instances/{id}/messages/{message_id}`

**Query**: `chat_id` (required)

**Response** `204`: No content

**Errors**:
- `400` instance not connected / message not owned by instance
- `403` cannot edit/delete other users' messages
- `404` instance or message not found
