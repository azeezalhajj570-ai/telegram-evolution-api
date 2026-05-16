# Feature Specification: Rich Messaging

**Feature Branch**: `002-rich-messaging`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "Extend Telegram Evolution API MVP with rich messaging features: send media, reply, forward, edit, delete, react to messages."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Send Media Messages (Priority: P1)

As a developer, I want to send photo, document, video, audio, and voice messages through the API so that my application can share rich content beyond plain text.

**Why this priority**: Media sending is the primary gap between the text-only MVP and a useful messaging API.

**Independent Test**: Can be tested by uploading a small image file via multipart/form-data to the send-photo endpoint and verifying the message appears in the destination chat.

**Acceptance Scenarios**:

1. **Given** a connected instance, **When** I POST a multipart/form-data request with a valid image file to `/instances/{id}/messages/send-photo`, **Then** the message is delivered and the response includes the message ID and chat ID.
2. **Given** a connected instance, **When** I send a document via `/instances/{id}/messages/send-document`, **Then** the file reaches the destination as a document message.
3. **Given** a connected instance, **When** I send a video via `/instances/{id}/messages/send-video`, **Then** Telegram displays it as a video message.
4. **Given** a connected instance, **When** I send audio via `/instances/{id}/messages/send-audio`, **Then** Telegram displays it as an audio track.
5. **Given** a connected instance, **When** I send a voice recording via `/instances/{id}/messages/send-voice`, **Then** Telegram displays it as a voice note.
6. **Given** a connected instance, **When** I send a file larger than Telegram's 50MB limit, **Then** the API returns a 413 error without uploading.
7. **Given** a disconnected instance, **When** I send any media message, **Then** the API returns a 400 error.

---

### User Story 2 - Message Actions: Reply, Forward, Edit, Delete (Priority: P1)

As a developer, I want to reply to, forward, edit, and delete messages through the API so that my application can implement full conversation workflows.

**Why this priority**: These actions are essential for building interactive bots and automation.

**Independent Test**: Can be tested by sending a text message, replying to it, forwarding the reply to another chat, editing the forwarded message text, then deleting it — all via API with a single connected instance.

**Acceptance Scenarios**:

1. **Given** an existing message, **When** I POST to `/instances/{id}/messages/reply` with the message ID and text, **Then** the reply is attached to the original message in the chat.
2. **Given** an existing message, **When** I POST to `/instances/{id}/messages/forward` with the message ID and a target chat, **Then** the message is forwarded to the target chat.
3. **Given** a message sent by the connected instance, **When** I PATCH `/instances/{id}/messages/{message_id}` with new text, **Then** the message text is updated in the chat.
4. **Given** a message sent by the connected instance, **When** I DELETE `/instances/{id}/messages/{message_id}`, **Then** the message is removed from the chat.
5. **Given** a message sent by another user, **When** I attempt to edit or delete it, **Then** the API returns a 403 error.

---

### User Story 3 - Message Reactions (Priority: P2)

As a developer, I want to add and remove emoji reactions on messages so that my application can support interactive engagement features.

**Why this priority**: Reactions are valuable but not critical for core messaging workflows.

**Independent Test**: Can be tested by sending a message, reacting with an emoji, and verifying the reaction appears via a chat query.

**Acceptance Scenarios**:

1. **Given** an existing message, **When** I POST to `/instances/{id}/messages/{message_id}/reaction` with a valid emoji, **Then** the reaction is applied to the message.
2. **Given** a message with an existing reaction, **When** I POST with an empty emoji or "remove", **Then** the reaction is removed.
3. **Given** a message in a chat where reactions are disabled, **When** I attempt to react, **Then** the API returns a 400 error.

---

### User Story 4 - Media Download (Priority: P2)

As a developer, I want to download media from received messages so that my application can process incoming files.

**Why this priority**: Media download enables content processing workflows.

**Independent Test**: Can be tested by sending an image to the connected account, then downloading it via the media endpoint and verifying the returned file matches.

**Acceptance Scenarios**:

1. **Given** a received message with media, **When** I GET `/instances/{id}/messages/{message_id}/media`, **Then** the API returns the media file with the correct MIME type.
2. **Given** a text message with no media, **When** I GET the media endpoint, **Then** the API returns a 404 error.
3. **Given** a media file that is too large (exceeds configured download limit), **When** I GET the media endpoint, **Then** the API returns a 413 error.

---

### Edge Cases

- What happens when the file upload is interrupted? The API returns a 400 error with details.
- What happens when a file format is unsupported? Telegram handles conversion; the API passes the file through.
- What happens when editing a message with media? Only caption text can be edited; the API returns an error if media fields are included.
- What happens when forwarding a message to a chat the instance is not a member of? Telegram returns a chat-not-found error, propagated to the caller.
- What happens when a reaction emoji is not supported by Telegram? Telegram ignores the reaction; the API returns success since the request was valid.
- What happens when deleting a message that was already deleted? The API returns a 404 error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept multipart/form-data file uploads for photo, document, video, audio, and voice messages.
- **FR-002**: The system MUST validate file size before uploading and reject files exceeding Telegram's limit (50MB) with a 413 error.
- **FR-003**: The system MUST store uploaded files temporarily and clean them up after sending.
- **FR-004**: The system MUST support optional caption text on media messages.
- **FR-005**: The system MUST support replying to an existing message by providing the replied-to message ID.
- **FR-006**: The system MUST support forwarding a message to another chat by providing the message ID and target chat ID.
- **FR-007**: The system MUST support editing message text via PATCH request.
- **FR-008**: The system MUST support deleting a message via DELETE request.
- **FR-009**: The system MUST support setting and removing emoji reactions on messages.
- **FR-010**: The system MUST support downloading media from received messages as a file stream.
- **FR-011**: The system MUST emit normalized webhook events for incoming media messages, including file metadata and download URL.
- **FR-012**: The system MUST reject edit/delete requests for messages not owned by the connected instance.

### Key Entities

- **MediaMessage**: A message that contains a file attachment (photo, document, video, audio, voice). Extends the message model with file metadata (file_id, mime_type, file_size, thumbnail).
- **MessageAction**: An operation applied to an existing message (reply, forward, edit, delete, reaction). Each action has its own request parameters and validation rules.

## Success Criteria *(mandatory)*

- **SC-001**: A developer can upload and send a 1MB image through the API and see it arrive in the destination chat within 15 seconds.
- **SC-002**: A developer can reply to a message, forward it, edit the forwarded copy, and delete the original in under 30 seconds total.
- **SC-003**: A developer can add a reaction to a message and verify it appears in less than 10 seconds.
- **SC-004**: A developer can download a received photo through the API and save it locally.
- **SC-005**: Uploading a 60MB file returns a 413 error in under 2 seconds without consuming significant memory.
- **SC-006**: Each endpoint returns appropriate HTTP status codes (200, 201, 400, 403, 404, 413).

## Assumptions

- Telegram's existing file size limits apply (photos ~10MB, documents up to 2GB for Premium, 50MB for free).
- The gateway stores uploaded files in a temporary directory (`/tmp/`).
- Temporary files are cleaned up after successful send or on error.
- Media download supports progressive streaming for large files.
- Reactions use standard emoji Unicode characters.
- The connected instance must be a member of the target chat for forward operations.
- Edit and delete operations only work on messages sent by the connected instance.
