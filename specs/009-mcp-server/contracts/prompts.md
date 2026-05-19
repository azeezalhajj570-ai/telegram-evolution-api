# MCP Prompt Contracts

Prompts use `@mcp.prompt()` registration. Each prompt is a pre-built template that helps AI agents with common Telegram workflows.

---

## compose_message

Helps compose a message tailored to a specific recipient and context.

```python
@mcp.prompt()
async def compose_message(
    recipient: str,
    context: str | None = None,
    tone: Literal["formal", "casual", "urgent"] = "casual",
) -> list[Message]:
    ...
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `recipient` | str | yes | Name or username of the message recipient |
| `context` | str | no | Context about what to communicate |
| `tone` | enum | no | Desired tone: formal, casual, or urgent |

**Template**:
```
Compose a message to {recipient}{ with this context: {context}} in a {tone} tone.

Consider:
- The relationship with {recipient}
- The context provided
- The desired tone ({tone})

Write the message:
```

---

## summarize_chat

Summarizes recent activity in a chat.

```python
@mcp.prompt()
async def summarize_chat(
    chat_id: int,
    hours: int = 24,
) -> list[Message]:
    ...
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `chat_id` | int | yes | The chat ID to summarize |
| `hours` | int | no | Number of hours to look back (default: 24) |

**Template**:
```
Summarize the recent activity in chat {chat_id} over the last {hours} hours.

Fetch the recent messages using the get_messages tool and provide:
- Key topics discussed
- Active participants
- Any decisions or action items
- Notable messages or events
```

---

## draft_reply

Drafts a reply to a specific message.

```python
@mcp.prompt()
async def draft_reply(
    chat_id: int,
    message_id: int,
) -> list[Message]:
    ...
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `chat_id` | int | yes | The chat containing the message |
| `message_id` | int | yes | The message ID to reply to |

**Template**:
```
Draft a reply to the following message in chat {chat_id}:

[Fetch message {message_id} content using get_messages]

Consider:
- The original message context
- Appropriate tone and length
- Whether any action is requested

Draft the reply:
```
