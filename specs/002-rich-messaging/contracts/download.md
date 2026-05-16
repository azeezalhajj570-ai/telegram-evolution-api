# Contract: Media Download

All endpoints require `X-API-Key` header.

## Download Media

`GET /instances/{id}/messages/{message_id}/media`

**Query**: `chat_id` (required)

**Response** `200`: Binary file stream with correct `Content-Type` and `Content-Disposition` headers.

**Errors**:
- `400` instance not connected / message has no media
- `404` instance or message not found
- `413` media exceeds download size limit
