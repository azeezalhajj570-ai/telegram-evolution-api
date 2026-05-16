# API Examples

Complete examples for common Telegram Evolution API workflows.

## Setup

```bash
export API_URL="http://localhost:8000"
export API_KEY="your-api-key-here"
```

## 1. Instance Management

### Create an Instance

```bash
curl -X POST "$API_URL/instances" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Telegram Account"}'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Telegram Account",
  "status": "disconnected",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### List Instances

```bash
curl "$API_URL/instances" \
  -H "Authorization: Bearer $API_KEY"
```

### Get Instance Status

```bash
curl "$API_URL/instances/$INSTANCE_ID" \
  -H "Authorization: Bearer $API_KEY"
```

### Delete an Instance

```bash
curl -X DELETE "$API_URL/instances/$INSTANCE_ID" \
  -H "Authorization: Bearer $API_KEY"
```

## 2. Authentication

### Send Login Code

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/auth/send-code" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'
```

Response:
```json
{
  "phone_code_hash": "abc123",
  "is_code_via_app": false
}
```

### Verify Code

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/auth/verify-code" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"code": "12345"}'
```

### Submit 2FA Password (if required)

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/auth/2fa" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"password": "my-2fa-password"}'
```

### Connect Instance

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/auth/connect" \
  -H "Authorization: Bearer $API_KEY"
```

## 3. Messaging

### Send Text Message

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/send-message" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "text": "Hello from Telegram Evolution API!"
  }'
```

### Send Photo

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/send-message/photo" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "file_path": "/path/to/photo.jpg",
    "caption": "Check out this photo!"
  }'
```

### Send Document

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/send-message/document" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "file_path": "/path/to/document.pdf",
    "caption": "Here is the document"
  }'
```

### Reply to Message

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/messages/reply" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "reply_to_msg_id": 42,
    "text": "Replying to your message!"
  }'
```

### Forward Message

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/messages/forward" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from_chat_id": 111111,
    "to_chat_id": 222222,
    "message_id": 42
  }'
```

### Edit Message

```bash
curl -X PUT "$API_URL/instances/$INSTANCE_ID/messages/$MESSAGE_ID" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Updated message text"}'
```

### Delete Message

```bash
curl -X DELETE "$API_URL/instances/$INSTANCE_ID/messages/$MESSAGE_ID" \
  -H "Authorization: Bearer $API_KEY"
```

### Add Reaction

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/messages/$MESSAGE_ID/reaction" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"emoji": "👍"}'
```

## 4. Contacts

### List Contacts

```bash
curl "$API_URL/instances/$INSTANCE_ID/contacts" \
  -H "Authorization: Bearer $API_KEY"
```

### Import Contact

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/contacts/import" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Delete Contact

```bash
curl -X DELETE "$API_URL/instances/$INSTANCE_ID/contacts/$CONTACT_ID" \
  -H "Authorization: Bearer $API_KEY"
```

## 5. Groups

### List Groups

```bash
curl "$API_URL/instances/$INSTANCE_ID/groups" \
  -H "Authorization: Bearer $API_KEY"
```

### Create Group

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/groups" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My New Group",
    "members": [123456789]
  }'
```

### Add Member to Group

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/groups/$GROUP_ID/members" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 987654321}'
```

### Remove Member from Group

```bash
curl -X DELETE "$API_URL/instances/$INSTANCE_ID/groups/$GROUP_ID/members/$USER_ID" \
  -H "Authorization: Bearer $API_KEY"
```

## 6. Channels

### List Channels

```bash
curl "$API_URL/instances/$INSTANCE_ID/channels" \
  -H "Authorization: Bearer $API_KEY"
```

### Join Channel

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/channels/join" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"channel_id": "@channelname"}'
```

### Leave Channel

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/channels/leave" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"channel_id": "@channelname"}'
```

### Browse Channel Messages

```bash
curl "$API_URL/instances/$INSTANCE_ID/channels/@channelname/messages?limit=50" \
  -H "Authorization: Bearer $API_KEY"
```

## 7. Webhooks

### Configure Webhook

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/webhook" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-app.com/webhook"}'
```

### Test Webhook

```bash
curl -X POST "$API_URL/instances/$INSTANCE_ID/webhook/test" \
  -H "Authorization: Bearer $API_KEY"
```

### Verify Webhook Signature (Python)

```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## 8. Organizations (Multi-Tenant)

### Create Organization

```bash
curl -X POST "$API_URL/orgs" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Acme Corp"}'
```

### Add Member to Organization

```bash
curl -X POST "$API_URL/orgs/$ORG_ID/members" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "role": "developer"
  }'
```

### Create Scoped API Key

```bash
curl -X POST "$API_URL/orgs/$ORG_ID/api-keys" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production-key",
    "scopes": ["instances:read", "messages:send"]
  }'
```

### View Audit Log

```bash
curl "$API_URL/orgs/$ORG_ID/audit-log?limit=100" \
  -H "Authorization: Bearer $API_KEY"
```

## 9. Health & Metrics

### Health Check

```bash
curl "$API_URL/health"
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600
}
```

### Prometheus Metrics

```bash
curl "$API_URL/metrics"
```

## 10. Error Handling

### Rate Limit Response

```json
{
  "error": "rate_limited",
  "detail": "Too many requests",
  "retry_after_seconds": 30
}
```

### FloodWait Response

```json
{
  "error": "flood_wait",
  "detail": "Telegram rate limit exceeded",
  "retry_after_seconds": 120
}
```

### Authentication Required

```json
{
  "error": "auth_required",
  "detail": "Instance requires authentication"
}
```
