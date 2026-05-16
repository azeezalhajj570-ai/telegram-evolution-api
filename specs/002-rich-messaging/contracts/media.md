# Contract: Media Messages

All endpoints require `X-API-Key` header. All use `multipart/form-data`.

## Send Photo

`POST /instances/{id}/messages/send-photo`

**Request** (multipart/form-data):
| Field | Type | Required |
|-------|------|----------|
| file | binary | yes |
| caption | str | no |
| chat_id | int | yes |

**Response** `200`:
```json
{"message_id": 42, "chat_id": 123, "type": "photo", "status": "delivered"}
```

## Send Document

`POST /instances/{id}/messages/send-document`

Same form fields. Response same shape with `"type": "document"`.

## Send Video

`POST /instances/{id}/messages/send-video`

Same form fields. Response same shape with `"type": "video"`.

## Send Audio

`POST /instances/{id}/messages/send-audio`

Same form fields. Response same shape with `"type": "audio"`.

## Send Voice

`POST /instances/{id}/messages/send-voice`

Same form fields. Response same shape with `"type": "voice"`.

**Errors** (all endpoints):
- `400` instance not connected
- `404` instance not found
- `413` file exceeds size limit
