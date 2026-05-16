# Contract: Reactions

All endpoints require `X-API-Key` header.

## Send/Remove Reaction

`POST /instances/{id}/messages/{message_id}/reaction`

**Request**:
```json
{"emoji": "👍"}
```

Pass empty string or `"remove"` to remove reaction.

**Response** `200`:
```json
{"message_id": 42, "reaction": "👍", "status": "applied"}
```

**Errors**:
- `400` instance not connected / reactions not available in chat
- `404` instance or message not found
