# Data Model: MCP Server

**Tool signatures, Resource URIs, Prompt templates, and error contracts.**

MCP is a protocol layer — no new database tables. All data flows through existing repositories and services.

---

## Entity: `MCPTool`

| Field | Type | Description |
|-------|------|-------------|
| name | str | Unique tool name in `snake_case` (e.g., `send_message`) |
| description | str | Human-readable description of what the tool does |
| input_schema | dict | JSON Schema object describing parameters |
| handler | Callable | Async function that executes the tool logic |
| domain | enum | Category: messaging, chats, contacts, groups, channels, instances, webhooks |

### Tool Registry

| Tool Name | Domain | Input Parameters | Output |
|-----------|--------|------------------|--------|
| `send_message` | messaging | `instance_id: str`, `chat_id: int`, `text: str` | `{"message_id": int, "chat_id": int, "status": "sent"}` |
| `send_media` | messaging | `instance_id: str`, `chat_id: int`, `file_path: str`, `caption?: str`, `media_type: str` | `{"message_id": int, "chat_id": int, "status": "sent"}` |
| `get_messages` | messaging | `instance_id: str`, `chat_id: int`, `limit?: int(default=20)`, `offset?: int` | `{"messages": [...]}` |
| `reply_message` | messaging | `instance_id: str`, `chat_id: int`, `reply_to_msg_id: int`, `text: str` | `{"message_id": int, "chat_id": int, "status": "replied"}` |
| `forward_message` | messaging | `instance_id: str`, `from_chat_id: int`, `to_chat_id: int`, `message_id: int` | `{"message_id": int, "status": "forwarded"}` |
| `edit_message` | messaging | `instance_id: str`, `chat_id: int`, `message_id: int`, `text: str` | `{"status": "edited"}` |
| `delete_message` | messaging | `instance_id: str`, `chat_id: int`, `message_id: int` | `{"status": "deleted"}` |
| `add_reaction` | messaging | `instance_id: str`, `chat_id: int`, `message_id: int`, `emoji: str` | `{"status": "reaction_added"}` |
| `list_chats` | chats | `instance_id: str`, `limit?: int(default=50)`, `offset?: int` | `{"chats": [...]}` |
| `get_chat_info` | chats | `instance_id: str`, `chat_id: int` | `{"chat": {...}}` |
| `search_messages` | chats | `instance_id: str`, `chat_id: int`, `query: str`, `limit?: int(default=20)` | `{"messages": [...]}` |
| `list_contacts` | contacts | `instance_id: str`, `limit?: int(default=100)` | `{"contacts": [...]}` |
| `import_contact` | contacts | `instance_id: str`, `phone: str`, `first_name: str`, `last_name?: str` | `{"contact": {...}}` |
| `delete_contact` | contacts | `instance_id: str`, `contact_id: int` | `{"status": "deleted"}` |
| `list_groups` | groups | `instance_id: str` | `{"groups": [...]}` |
| `create_group` | groups | `instance_id: str`, `title: str`, `member_ids?: list[int]` | `{"group_id": int, "status": "created"}` |
| `add_group_member` | groups | `instance_id: str`, `group_id: int`, `user_id: int` | `{"status": "added"}` |
| `remove_group_member` | groups | `instance_id: str`, `group_id: int`, `user_id: int` | `{"status": "removed"}` |
| `list_channels` | channels | `instance_id: str` | `{"channels": [...]}` |
| `join_channel` | channels | `instance_id: str`, `channel_id: int` | `{"status": "joined"}` |
| `leave_channel` | channels | `instance_id: str`, `channel_id: int` | `{"status": "left"}` |
| `create_instance` | instances | `name: str` | `{"id": str, "name": str, "status": "pending"}` |
| `list_instances` | instances | — | `{"instances": [...]}` |
| `get_instance_status` | instances | `instance_id: str` | `{"id": str, "name": str, "status": str}` |
| `send_auth_code` | instances | `instance_id: str`, `phone_number: str` | `{"status": "code_sent"}` |
| `verify_auth_code` | instances | `instance_id: str`, `code: str` | `{"status": "authenticated"}` (or `"awaiting_2fa"`) |
| `submit_2fa` | instances | `instance_id: str`, `password: str` | `{"status": "authenticated"}` |
| `connect_instance` | instances | `instance_id: str` | `{"status": "connected"}` |
| `set_instance_api_key` | instances | `instance_id: str` | `{"instance_id": str, "api_key": str, "status": "created"}` |
| `get_scoped_instance` | instances | — | `{"instance_id": str \| null}` |
| `configure_webhook` | webhooks | `instance_id: str`, `url: str` | `{"webhook_id": str, "status": "configured"}` |
| `test_webhook` | webhooks | `instance_id: str` | `{"status": str, "status_code": int}` |

---

## Entity: `MCPResource`

| Field | Type | Description |
|-------|------|-------------|
| uri_template | str | URI pattern with `{param}` placeholders |
| name | str | Human-readable resource name |
| description | str | What data the resource provides |
| mime_type | str | Content type (default: `application/json`) |
| handler | Callable | Async function returning resource content |

### Resource URIs

| URI Template | Name | Description |
|-------------|------|-------------|
| `telegram://instances` | All Instances | List of all instances with status, phone, and connection state |
| `telegram://instances/{instance_id}` | Single Instance | Detailed info for one instance |
| `telegram://chats` | Recent Chats | Recent dialogs across all connected instances |
| `telegram://chats/{chat_id}` | Chat Details | Details of a specific chat |
| `telegram://contacts` | Contact List | All contacts from the active/default instance |
| `telegram://messages/{chat_id}` | Chat Messages | Recent messages in a specific chat |
| `telegram://messages/{chat_id}/{message_id}` | Single Message | Details of a single message |

---

## Entity: `MCPPrompt`

| Field | Type | Description |
|-------|------|-------------|
| name | str | Unique prompt name |
| description | str | What the prompt helps with |
| arguments | list[PromptArgument] | Template arguments with types |
| template | str | Prompt text with `{arg}` placeholders |

### Prompt Templates

| Prompt Name | Arguments | Description |
|-------------|-----------|-------------|
| `compose_message` | `recipient: str`, `context?: str`, `tone?: str` | Help compose a message for a specific recipient and context with a given tone (formal/casual/urgent) |
| `summarize_chat` | `chat_id: int`, `hours?: int(default=24)` | Summarize recent activity in a chat over the last N hours |
| `draft_reply` | `chat_id: int`, `message_id: int` | Draft a reply to a specific message in context |

---

## Error Mapping

| Telegram Error | MCP Error Code | User-Friendly Message |
|---------------|----------------|----------------------|
| `FloodWaitError(seconds=X)` | `-32000` (rate_limited) | "Rate limited by Telegram. Try again in X seconds." |
| `RPCCallFailError` | `-32001` (telegram_error) | "Telegram request failed. Please try again." |
| `ChatIdInvalidError` | `-32002` (invalid_chat) | "Chat not found. Check the chat ID and try again." |
| `MessageIdInvalidError` | `-32003` (invalid_message) | "Message not found. It may have been deleted." |
| `AuthKeyUnregisteredError` | `-32004` (not_connected) | "Instance is disconnected. Please re-authenticate." |
| `PhoneCodeInvalidError` | `-32005` (invalid_code) | "Invalid verification code. Please check and try again." |
| `SessionPasswordNeededError` | `-32006` (2fa_required) | "2FA is enabled. Please submit your 2FA password." |
| `PhoneNumberBannedError` | `-32007` (banned) | "This phone number has been banned by Telegram." |
| `ValueError` (not connected) | `-32008` (not_connected) | "Instance is not connected. Call connect_instance first." |
| Generic `RPCError` | `-32099` (unknown_rpc) | "Telegram API error: {message}" |

### MCP Standard Error Codes Used

| Code | Meaning | When |
|------|---------|------|
| `-32700` | Parse error | Invalid JSON-RPC request |
| `-32600` | Invalid request | Malformed tool call |
| `-32601` | Method not found | Unknown tool name |
| `-32602` | Invalid params | Schema validation failed |
| `-32603` | Internal error | Unexpected server error |
| `-32000` to `-32099` | Server errors | Telegram-specific errors (see mapping above) |
