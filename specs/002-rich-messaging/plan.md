# Implementation Plan: Rich Messaging

**Branch**: `002-rich-messaging` | **Date**: 2026-05-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-rich-messaging/spec.md`

## Summary

Extend the Telegram API Gateway with rich messaging: send media (photo, document, video, audio, voice), reply/forward/edit/delete messages, react with emoji, and download received media.

## Technical Context

**Language/Version**: Python 3.9+ (same as MVP)

**Primary Dependencies**: python-multipart (file uploads), aiofiles (temp file I/O), Telethon (media send, message actions)

**Storage**: File system (`/tmp/` for temporary uploads), PostgreSQL (no new tables — existing instance model)

**Testing**: pytest, pytest-asyncio, unittest.mock (mocked Telethon client)

**Target Platform**: Linux (Docker Compose)

**Project Type**: web-service (REST API — extends existing MVP)

**Performance Goals**: Upload + send a 1MB photo in under 15 seconds; sub-1s for reply/forward/edit/delete

**Constraints**: <200ms p95 API response excluding Telegram network; max upload 50MB; temp files cleaned after send; no permanent file storage unless configured

**Scale/Scope**: Single server, extends existing MVP codebase

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Code Quality** ✅ — Existing patterns: Pydantic schemas, service layer, repository pattern
**II. Testing Standards** ✅ — 3 new test files with mocked Telethon for every endpoint
**III. User Experience Consistency** ✅ — Consistent REST paths under `/instances/{id}/messages/`
**IV. Performance Requirements** ✅ — Async file I/O, stream uploads, temp file cleanup
**V. Security & Observability** ✅ — Validate file size before write, sanitize filenames, structured error responses

**GATE RESULT**: PASS ✅

## Project Structure

### Documentation

```
specs/002-rich-messaging/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/           # Phase 1
│   ├── media.md
│   ├── actions.md
│   ├── reactions.md
│   └── download.md
└── tasks.md             # Phase 2
```

### Source Code — New/Modified Files

```text
app/
├── schemas/
│   └── media.py              # NEW — file upload request/response schemas
├── api/
│   └── messages.py            # MODIFY — add media, reply, forward, edit, delete, reaction endpoints
├── services/
│   └── messaging.py           # MODIFY — add send_media, reply, forward, edit, delete, react methods
tests/
├── test_media.py              # NEW — media send + download tests
├── test_message_actions.py    # NEW — reply, forward, edit, delete tests
└── test_reactions.py          # NEW — reaction tests
```

## Complexity Tracking

No constitution violations.

## Phase 0 — Research

**No unknowns** — tech stack is already established from Phase 1 MVP. Key findings:
- `python-multipart` is required for FastAPI `UploadFile` support (already works out of box with FastAPI)
- Telethon `client.send_file()` handles ALL media types (photo, document, video, audio, voice)
- Telethon `client.send_message()` supports `reply_to` parameter for replies
- Telethon `client.forward_messages()` for forwarding
- Telethon `client.edit_message()` for editing
- Telethon `client.delete_messages()` for deleting
- Telethon `client.send_reaction()` for reactions (Telethon >= 1.33)
- Telethon `client.download_media()` for media download
- File size validation must happen BEFORE write to disk

## Phase 1 — Design & Contracts

**Prerequisites**: research.md complete.

**Generated artifacts**:
1. `data-model.md` — request/response schemas, no new DB entities
2. `contracts/` — REST API contracts for all new endpoints
3. `quickstart.md` — updated testing notes
4. `AGENTS.md` — plan reference update
