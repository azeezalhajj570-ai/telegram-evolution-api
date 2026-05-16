# Research: Rich Messaging — Technology Decisions

**Phase 0 Output** — All decisions confirmed from existing MVP stack.

## File Uploads

| Decision | Rationale |
|----------|-----------|
| **FastAPI UploadFile** | Built-in multipart support via `python-multipart`. Streams to disk automatically. |
| **Temp file path** | `/tmp/telegram_uploads/` — cleaned after each send. Configurable via env. |
| **Max file size** | 50MB — Telegram's free account limit. Checked via `Content-Length` header before reading. |

## Media Sending (Telethon)

| Endpoint | Telethon API |
|----------|-------------|
| send-photo | `client.send_file(chat, file, caption=...)` with `file` as file path |
| send-document | `client.send_file(chat, file, caption=...)` — Telethon auto-detects type |
| send-video | `client.send_file(chat, file, caption=...)` |
| send-audio | `client.send_file(chat, file, caption=..., attributes=[AudioAttributes])` |
| send-voice | `client.send_file(chat, file, attributes=[VoiceAttributes])` |

## Message Actions (Telethon)

| Action | Telethon API |
|--------|-------------|
| Reply | `client.send_message(chat, text, reply_to=msg_id)` |
| Forward | `client.forward_messages(target_chat, msg_ids, source_chat)` |
| Edit | `client.edit_message(chat, msg_id, text)` |
| Delete | `client.delete_messages(chat, msg_ids)` |
| React | `client.send_reaction(chat, msg_id, reaction=emoji)` |
| Download | `client.download_media(message, file=path)` |

## Testing Strategy

| Test Type | Approach |
|-----------|----------|
| Media send | Mock `telethon.TelegramClient.send_file` with AsyncMock |
| Message actions | Mock each Telethon method individually |
| Reactions | Mock `client.send_reaction` |
| Download | Mock `client.download_media` |
| File validation | Unit test with oversized payload |
