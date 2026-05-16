---
description: "Implementation tasks for Rich Messaging feature"
---

# Tasks: Rich Messaging

**Input**: Design documents from `/specs/002-rich-messaging/`

**Tests**: Tests are MANDATORY per the project constitution.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: Which user story this task belongs to

---

## Phase 1: Setup

- [ ] T001 Add `python-multipart` and `aiofiles` to `pyproject.toml` dependencies
- [ ] T002 Create temp upload directory `app/utils/file_utils.py` — helper for saving UploadFile to temp path, validating file size (<50MB), generating unique filenames, and cleaning up after send

---

## Phase 2: User Story 1 — Send Media (Priority: P1) 🎯

**Goal**: Send photo, document, video, audio, and voice messages via multipart upload

**Independent Test**: Upload a small image to send-photo and verify it arrives in the chat

### Implementation

- [ ] T003 [P] [US1] Create media Pydantic schemas in `app/schemas/media.py` — `MediaMessageResponse` (message_id, chat_id, type, status) and `FileSizeError` constants
- [ ] T004 [US1] Add `send_photo`, `send_document`, `send_video`, `send_audio`, `send_voice` methods to `app/services/messaging.py` — each accepts instance_id, chat_id, file_path, optional caption; calls `client.send_file()` with appropriate attributes
- [ ] T005 [US1] Add media send API endpoints in `app/api/messages.py` — `POST /instances/{id}/messages/send-{type}` accepting `UploadFile` + `chat_id` + `caption` as multipart/form-data; validates file size, saves to temp, calls messaging service, cleans up temp file after
- [ ] T006 [US1] Add file size validation in `app/api/messages.py` — reject files >50MB before reading, return `413` with clear message

---

## Phase 3: User Story 2 — Message Actions (Priority: P1)

**Goal**: Reply, forward, edit, delete messages

**Independent Test**: Send a message, reply to it, forward the reply, edit it, then delete it

### Implementation

- [ ] T007 [P] [US2] Create action schemas in `app/schemas/media.py` — `ReplyRequest`, `ForwardRequest`, `EditMessageRequest`, `MessageActionResponse`
- [ ] T008 [US2] Add `reply_message`, `forward_message`, `edit_message`, `delete_message` methods to `app/services/messaging.py` — each calls the corresponding Telethon API method
- [ ] T009 [US2] Add action API endpoints in `app/api/messages.py`:
  - `POST /instances/{id}/messages/reply`
  - `POST /instances/{id}/messages/forward`
  - `PATCH /instances/{id}/messages/{message_id}`
  - `DELETE /instances/{id}/messages/{message_id}?chat_id=X`

---

## Phase 4: User Story 3 — Reactions (Priority: P2)

**Goal**: Add and remove emoji reactions on messages

**Independent Test**: Send a message, react with 👍, verify reaction via chat query

- [ ] T010 [P] [US3] Create reaction schemas in `app/schemas/media.py` — `ReactionRequest`, `ReactionResponse`
- [ ] T011 [US3] Add `send_reaction` method to `app/services/messaging.py` — calls `client.send_reaction()`, handles remove by passing empty string
- [ ] T012 [US3] Add reaction API endpoint `POST /instances/{id}/messages/{message_id}/reaction` in `app/api/messages.py`

---

## Phase 5: User Story 4 — Media Download (Priority: P2)

**Goal**: Download media from received messages

**Independent Test**: Send a photo to the instance, then download it via the API

- [ ] T013 [P] [US4] Create download schemas — `MediaDownloadResponse` (StreamingResponse wrapper)
- [ ] T014 [US4] Add `download_media` method to `app/services/messaging.py` — calls `client.download_media()`, returns file path, streams to response
- [ ] T015 [US4] Add download endpoint `GET /instances/{id}/messages/{message_id}/media?chat_id=X` in `app/api/messages.py` — returns `StreamingResponse` with correct MIME type

---

## Phase 6: Tests

- [ ] T016 [P] Write `tests/test_media.py` — test each media send endpoint with mocked `client.send_file`, test file size validation (413), test disconnected instance (400), test missing file (422)
- [ ] T017 [P] Write `tests/test_message_actions.py` — test reply, forward, edit, delete with mocked Telethon methods, test unauthorized edit/delete (403)
- [ ] T018 [P] Write `tests/test_reactions.py` — test add reaction, remove reaction, reaction in unsupported chat

---

## Dependencies

- **Phase 1**: No deps — can start immediately
- **US1 (P1)**: Blocks US2, US3, US4 (all need messaging service)
- **US2 (P1)**: Depends on US1 (needs Telethon client)
- **US3 (P2)**: Depends on US1
- **US4 (P2)**: Depends on US1
- **Tests**: Blocked until all implementation phases complete
