# MCP Resource Contracts

Resources use `@mcp.resource(uri_template)` registration. Each resource exposes Telegram data as `application/json` content.

---

## telegram://instances

List of all instances with status.

```python
@mcp.resource("telegram://instances")
async def get_instances() -> list[dict]:
    ...
```

**Output**:
```json
[
  {
    "uri": "telegram://instances/abc-123",
    "mimeType": "application/json",
    "name": "My Work Account",
    "description": "Telegram instance",
    "text": "{\"id\": \"abc-123\", \"name\": \"My Work Account\", \"status\": \"connected\", \"phone_number\": \"+5511999999999\"}"
  }
]
```

---

## telegram://instances/{instance_id}

Details of a specific instance.

```python
@mcp.resource("telegram://instances/{instance_id}")
async def get_instance(instance_id: str) -> dict:
    ...
```

---

## telegram://chats

Recent chats from all connected instances.

```python
@mcp.resource("telegram://chats")
async def get_chats() -> list[dict]:
    ...
```

**Output**:
```json
[
  {
    "uri": "telegram://chats/67890",
    "mimeType": "application/json",
    "name": "Group Chat",
    "description": "Telegram chat",
    "text": "{\"chat_id\": 67890, \"title\": \"Group Chat\", \"type\": \"group\", \"unread_count\": 3}"
  }
]
```

---

## telegram://chats/{chat_id}

Details of a specific chat.

```python
@mcp.resource("telegram://chats/{chat_id}")
async def get_chat(chat_id: int) -> dict:
    ...
```

---

## telegram://contacts

Contact list from the default/active instance.

```python
@mcp.resource("telegram://contacts")
async def get_contacts() -> list[dict]:
    ...
```

---

## telegram://messages/{chat_id}

Recent messages in a specific chat.

```python
@mcp.resource("telegram://messages/{chat_id}")
async def get_messages(chat_id: int) -> list[dict]:
    ...
```

---

## telegram://messages/{chat_id}/{message_id}

A single message.

```python
@mcp.resource("telegram://messages/{chat_id}/{message_id}")
async def get_message(chat_id: int, message_id: int) -> dict:
    ...
```
