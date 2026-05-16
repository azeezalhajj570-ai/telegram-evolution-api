# Data Model: Rich Messaging

**No new database entities.** All changes are in schemas and service methods.

## Request Schemas

### MediaMessageRequest (multipart/form-data)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | UploadFile | yes | The file to send |
| caption | str | no | Optional text caption (0-1024 chars) |
| chat_id | int | yes | Destination chat ID |

### ReplyRequest (application/json)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| chat_id | int | yes | Chat containing the message to reply to |
| text | str | yes | Reply text (1-4096 chars) |
| reply_to | int | yes | Message ID to reply to |

### ForwardRequest (application/json)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| from_chat_id | int | yes | Source chat ID |
| message_id | int | yes | Message ID to forward |
| to_chat_id | int | yes | Target chat ID |

### EditMessageRequest (application/json)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | str | yes | New message text |

### DeleteMessageRequest (application/json)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| chat_id | int | yes | Chat containing the message |

### ReactionRequest (application/json)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| emoji | str | yes | Emoji to react with (empty to remove) |

## Response Schemas

### MediaMessageResponse

```json
{
  "message_id": 42,
  "chat_id": 123456789,
  "type": "photo",
  "status": "delivered"
}
```

### MessageActionResponse

```json
{
  "message_id": 43,
  "status": "delivered"
}
```
