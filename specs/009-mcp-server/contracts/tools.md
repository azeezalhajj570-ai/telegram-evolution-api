# MCP Tool Contracts

All tools use `@mcp.tool()` registration. Parameters are auto-converted to JSON Schema from Python type hints.

---

## send_message

Send a text message to a Telegram chat.

```python
@mcp.tool()
async def send_message(
    instance_id: str,
    chat_id: int,
    text: str = Field(..., min_length=1, max_length=4096),
) -> dict:
    ...
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "instance_id": { "type": "string", "description": "ID of the Telegram instance" },
    "chat_id": { "type": "integer", "description": "Target chat ID" },
    "text": { "type": "string", "description": "Message text (1-4096 chars)", "minLength": 1, "maxLength": 4096 }
  },
  "required": ["instance_id", "chat_id", "text"]
}
```

**Output**:
```json
{ "message_id": 12345, "chat_id": 67890, "status": "sent" }
```

---

## send_media

Send a photo, document, or video to a chat.

```python
@mcp.tool()
async def send_media(
    instance_id: str,
    chat_id: int,
    file_path: str,
    caption: str | None = None,
    media_type: Literal["photo", "document", "video"] = "photo",
) -> dict:
    ...
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "instance_id": { "type": "string" },
    "chat_id": { "type": "integer" },
    "file_path": { "type": "string", "description": "Path or URL to the file" },
    "caption": { "type": "string", "description": "Optional caption" },
    "media_type": { "type": "string", "enum": ["photo", "document", "video"], "default": "photo" }
  },
  "required": ["instance_id", "chat_id", "file_path"]
}
```

**Output**:
```json
{ "message_id": 12345, "chat_id": 67890, "status": "sent" }
```

---

## get_messages

Get recent messages from a chat.

```python
@mcp.tool()
async def get_messages(
    instance_id: str,
    chat_id: int,
    limit: int = Field(default=20, ge=1, le=100),
    offset: int | None = None,
) -> dict:
    ...
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "instance_id": { "type": "string" },
    "chat_id": { "type": "integer" },
    "limit": { "type": "integer", "default": 20, "minimum": 1, "maximum": 100 },
    "offset": { "type": "integer", "description": "Message offset ID for pagination" }
  },
  "required": ["instance_id", "chat_id"]
}
```

**Output**:
```json
{
  "messages": [
    {
      "message_id": 12345,
      "chat_id": 67890,
      "sender_id": 11111,
      "sender_name": "John Doe",
      "text": "Hello!",
      "date": "2026-05-19T12:00:00Z",
      "is_outgoing": false
    }
  ]
}
```

---

## reply_message

Reply to a specific message.

```python
@mcp.tool()
async def reply_message(
    instance_id: str,
    chat_id: int,
    reply_to_msg_id: int,
    text: str = Field(..., min_length=1, max_length=4096),
) -> dict:
    ...
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "instance_id": { "type": "string" },
    "chat_id": { "type": "integer" },
    "reply_to_msg_id": { "type": "integer", "description": "Message ID to reply to" },
    "text": { "type": "string", "minLength": 1, "maxLength": 4096 }
  },
  "required": ["instance_id", "chat_id", "reply_to_msg_id", "text"]
}
```

**Output**:
```json
{ "message_id": 12346, "chat_id": 67890, "status": "replied" }
```

---

## forward_message

Forward a message to another chat.

```python
@mcp.tool()
async def forward_message(
    instance_id: str,
    from_chat_id: int,
    to_chat_id: int,
    message_id: int,
) -> dict:
    ...
```

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "instance_id": { "type": "string" },
    "from_chat_id": { "type": "integer" },
    "to_chat_id": { "type": "integer" },
    "message_id": { "type": "integer" }
  },
  "required": ["instance_id", "from_chat_id", "to_chat_id", "message_id"]
}
```

**Output**:
```json
{ "message_id": 12347, "status": "forwarded" }
```

---

## edit_message

Edit a previously sent message.

```python
@mcp.tool()
async def edit_message(
    instance_id: str,
    chat_id: int,
    message_id: int,
    text: str = Field(..., min_length=1, max_length=4096),
) -> dict:
    ...
```

**Output**: `{ "status": "edited" }`

---

## delete_message

Delete a message from a chat.

```python
@mcp.tool()
async def delete_message(
    instance_id: str,
    chat_id: int,
    message_id: int,
) -> dict:
    ...
```

**Output**: `{ "status": "deleted" }`

---

## add_reaction

Add an emoji reaction to a message.

```python
@mcp.tool()
async def add_reaction(
    instance_id: str,
    chat_id: int,
    message_id: int,
    emoji: str = Field(..., description="Emoji character, e.g. 👍, ❤️, 😂"),
) -> dict:
    ...
```

**Output**: `{ "status": "reaction_added" }`

---

## list_chats

List recent chats for an instance.

```python
@mcp.tool()
async def list_chats(
    instance_id: str,
    limit: int = Field(default=50, ge=1, le=200),
    offset: int | None = None,
) -> dict:
    ...
```

**Output**:
```json
{
  "chats": [
    {
      "chat_id": 67890,
      "title": "Group Chat",
      "type": "group",
      "unread_count": 3,
      "last_message": { "text": "Hey!", "date": "2026-05-19T12:00:00Z" }
    }
  ]
}
```

---

## get_chat_info

Get details about a specific chat.

```python
@mcp.tool()
async def get_chat_info(
    instance_id: str,
    chat_id: int,
) -> dict:
    ...
```

**Output**:
```json
{
  "chat": {
    "chat_id": 67890,
    "title": "Group Chat",
    "type": "group",
    "participants_count": 15,
    "description": "A group about...",
    "photo": null
  }
}
```

---

## search_messages

Search messages in a chat.

```python
@mcp.tool()
async def search_messages(
    instance_id: str,
    chat_id: int,
    query: str,
    limit: int = Field(default=20, ge=1, le=100),
) -> dict:
    ...
```

**Output**: Same as `get_messages` output shape.

---

## list_contacts

List all contacts.

```python
@mcp.tool()
async def list_contacts(
    instance_id: str,
    limit: int = Field(default=100, ge=1, le=500),
) -> dict:
    ...
```

**Output**:
```json
{
  "contacts": [
    {
      "contact_id": 11111,
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+5511999999999"
    }
  ]
}
```

---

## import_contact

Import a contact by phone number.

```python
@mcp.tool()
async def import_contact(
    instance_id: str,
    phone: str,
    first_name: str,
    last_name: str | None = None,
) -> dict:
    ...
```

---

## delete_contact

Delete a contact.

```python
@mcp.tool()
async def delete_contact(
    instance_id: str,
    contact_id: int,
) -> dict:
    ...
```

---

## list_groups

List groups the user is a member of.

```python
@mcp.tool()
async def list_groups(instance_id: str) -> dict:
    ...
```

---

## create_group

Create a new group.

```python
@mcp.tool()
async def create_group(
    instance_id: str,
    title: str = Field(..., min_length=1, max_length=128),
    member_ids: list[int] | None = None,
) -> dict:
    ...
```

---

## add_group_member / remove_group_member

```python
@mcp.tool()
async def add_group_member(instance_id: str, group_id: int, user_id: int) -> dict: ...
@mcp.tool()
async def remove_group_member(instance_id: str, group_id: int, user_id: int) -> dict: ...
```

---

## list_channels / join_channel / leave_channel

```python
@mcp.tool()
async def list_channels(instance_id: str) -> dict: ...
@mcp.tool()
async def join_channel(instance_id: str, channel_id: int) -> dict: ...
@mcp.tool()
async def leave_channel(instance_id: str, channel_id: int) -> dict: ...
```

---

## create_instance

```python
@mcp.tool()
async def create_instance(
    name: str = Field(..., min_length=1, max_length=256),
) -> dict:
    ...
```

**Output**:
```json
{ "id": "uuid", "name": "My Account", "status": "pending" }
```

---

## list_instances

```python
@mcp.tool()
async def list_instances() -> dict:
    ...
```

**Output**:
```json
{ "instances": [{ "id": "uuid", "name": "...", "status": "connected", "phone_number": "...", "created_at": "..." }] }
```

---

## get_instance_status

```python
@mcp.tool()
async def get_instance_status(instance_id: str) -> dict:
    ...
```

---

## send_auth_code

```python
@mcp.tool()
async def send_auth_code(instance_id: str, phone_number: str) -> dict:
    ...
```

**Output**: `{ "status": "code_sent" }`

---

## verify_auth_code

```python
@mcp.tool()
async def verify_auth_code(instance_id: str, code: str) -> dict:
    ...
```

**Output**: `{ "status": "authenticated" }` or `{ "status": "awaiting_2fa" }`

---

## submit_2fa

```python
@mcp.tool()
async def submit_2fa(instance_id: str, password: str) -> dict:
    ...
```

---

## connect_instance

```python
@mcp.tool()
async def connect_instance(instance_id: str) -> dict:
    ...
```

---

## configure_webhook / test_webhook

```python
@mcp.tool()
async def configure_webhook(instance_id: str, url: str) -> dict: ...
@mcp.tool()
async def test_webhook(instance_id: str) -> dict: ...
```
