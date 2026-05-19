# Feature Specification: MCP Server

**Feature Branch**: `009-mcp-server`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "Add MCP (Model Context Protocol) server support so AI agents can interact with RelayStack API natively through tools like Claude Desktop, Cursor, and other MCP-compatible clients."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - MCP Server Setup (Priority: P1)

As a developer using AI assistants, I want to configure the RelayStack API as an MCP server so that my AI agent can directly interact with my Telegram accounts.

**Why this priority**: Without the MCP server running and discoverable, no other MCP features work.

**Independent Test**: Can be tested by starting the MCP server, connecting an MCP client (e.g., Claude Desktop), and verifying the server advertises its tools correctly.

**Acceptance Scenarios**:

1. **Given** a running RelayStack API, **When** I start the MCP server, **Then** it exposes a stdio and/or SSE transport endpoint.
2. **Given** an MCP client configuration, **When** I add the Telegram MCP server config, **Then** the client discovers all available tools.
3. **Given** an MCP server running, **When** I request the tools list, **Then** it returns all registered tools with descriptions and JSON schemas.
4. **Given** the MCP server is configured with an API key, **When** a tool is called, **Then** the request is authenticated against the Telegram API.

---

### User Story 2 - Core Messaging Tools (Priority: P1)

As an AI agent user, I want my AI assistant to send, read, and manage Telegram messages so that I can interact with Telegram through natural language.

**Why this priority**: Messaging is the primary use case — this is what users will test first.

**Independent Test**: Can be tested by asking an AI agent to "send a message to @username saying hello" and verifying the message is delivered.

**Acceptance Scenarios**:

1. **Given** a connected Telegram instance, **When** I ask my AI agent to send a message, **Then** the message is delivered to the target chat.
2. **Given** a chat with unread messages, **When** I ask my AI agent to read recent messages, **Then** it returns the last N messages with sender info.
3. **Given** a message ID, **When** I ask my AI agent to delete a message, **Then** the message is removed from the chat.
4. **Given** a message ID, **When** I ask my AI agent to edit a message, **Then** the message text is updated.

---

### User Story 3 - Contact & Chat Management Tools (Priority: P2)

As an AI agent user, I want my AI assistant to manage contacts and browse chats so that I can organize my Telegram account through conversation.

**Why this priority**: Essential for discovering who to message and managing conversations.

**Independent Test**: Can be tested by asking an AI agent to "list my contacts" or "show my recent chats" and verifying correct results.

**Acceptance Scenarios**:

1. **Given** a connected instance, **When** I ask my AI agent to list contacts, **Then** it returns contacts with names and phone numbers.
2. **Given** a connected instance, **When** I ask my AI agent to list recent chats, **Then** it returns chats sorted by last message time.
3. **Given** a contact's phone number, **When** I ask my AI agent to add a contact, **Then** the contact is imported to Telegram.
4. **Given** a group chat, **When** I ask my AI agent to list group members, **Then** it returns the member list.

---

### User Story 4 - Instance Management Tools (Priority: P2)

As an AI agent user, I want my AI assistant to manage Telegram instances so that I can authenticate and configure accounts through conversation.

**Why this priority**: Users need to set up and manage instances without leaving their AI chat.

**Independent Test**: Can be tested by asking an AI agent to "create a new instance" and "check instance status."

**Acceptance Scenarios**:

1. **Given** no instances exist, **When** I ask my AI agent to create an instance, **Then** a new instance is created and returned.
2. **Given** an instance in "disconnected" status, **When** I ask my AI agent to authenticate it, **Then** the auth flow begins (code sent, waiting for verification).
3. **Given** a received Telegram code, **When** I tell my AI agent the code, **Then** the instance is verified and connected.
4. **Given** multiple instances, **When** I ask my AI agent to list instances, **Then** it returns all instances with their statuses.

---

### User Story 5 - Webhook & Event Streaming (Priority: P3)

As an AI agent user, I want my AI assistant to receive real-time Telegram events so that it can react to incoming messages and updates.

**Why this priority**: Enables proactive AI behavior (responding to messages, monitoring channels).

**Independent Test**: Can be tested by sending a message to the Telegram account and verifying the MCP client receives the event.

**Acceptance Scenarios**:

1. **Given** an MCP client connected with streaming enabled, **When** a new Telegram message arrives, **Then** the client receives a notification.
2. **Given** a connected instance, **When** I ask my AI agent to monitor a specific chat, **Then** it notifies me of new messages in that chat.
3. **Given** the MCP server supports subscriptions, **When** I subscribe to message events, **Then** I receive real-time updates.

---

### Edge Cases

- What happens when the Telegram instance is disconnected? Tools return a clear error suggesting re-authentication.
- What happens when a tool call exceeds Telegram rate limits? The MCP tool returns the `retry_after_seconds` value.
- What happens when the user asks for a chat that doesn't exist? The tool returns a helpful error with suggestions.
- What happens with large message histories? Results are paginated with a `limit` parameter (default 20).
- What happens when multiple instances exist? Tools require an `instance_id` parameter; if omitted, the default/active instance is used.
- What happens with media messages? Text content is returned; media files include download URLs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST implement the Model Context Protocol (MCP) specification v1.0+.
- **FR-002**: The system MUST support stdio transport for local AI clients (Claude Desktop, Cursor, etc.).
- **FR-003**: The system MUST support SSE transport for remote MCP clients.
- **FR-004**: The system MUST expose all tools with clear descriptions and JSON Schema parameters.
- **FR-005**: The system MUST support resources (chats, contacts, messages) that AI agents can read.
- **FR-006**: The system MUST support prompts (pre-built interaction templates) for common workflows.
- **FR-007**: The system MUST authenticate tool calls using the configured API key.
- **FR-008**: The system MUST handle errors gracefully and return user-friendly error messages.
- **FR-009**: The system MUST support pagination for list operations (contacts, chats, messages).
- **FR-010**: The system MUST expose instance status as a resource for monitoring.

### MCP Tools

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `send_message` | Send a text message to a chat | `instance_id`, `chat_id`, `text` |
| `send_media` | Send a photo/document/video to a chat | `instance_id`, `chat_id`, `file_path`, `caption`, `media_type` |
| `get_messages` | Get recent messages from a chat | `instance_id`, `chat_id`, `limit`, `offset` |
| `reply_message` | Reply to a specific message | `instance_id`, `chat_id`, `reply_to_msg_id`, `text` |
| `forward_message` | Forward a message to another chat | `instance_id`, `from_chat_id`, `to_chat_id`, `message_id` |
| `edit_message` | Edit a previously sent message | `instance_id`, `chat_id`, `message_id`, `text` |
| `delete_message` | Delete a message from a chat | `instance_id`, `chat_id`, `message_id` |
| `add_reaction` | Add an emoji reaction to a message | `instance_id`, `chat_id`, `message_id`, `emoji` |
| `list_chats` | List recent chats | `instance_id`, `limit`, `offset` |
| `get_chat_info` | Get details about a specific chat | `instance_id`, `chat_id` |
| `list_contacts` | List all contacts | `instance_id`, `limit` |
| `import_contact` | Import a contact by phone number | `instance_id`, `phone`, `first_name`, `last_name` |
| `delete_contact` | Delete a contact | `instance_id`, `contact_id` |
| `list_groups` | List groups the user is a member of | `instance_id` |
| `create_group` | Create a new group | `instance_id`, `title`, `member_ids` |
| `add_group_member` | Add a member to a group | `instance_id`, `group_id`, `user_id` |
| `remove_group_member` | Remove a member from a group | `instance_id`, `group_id`, `user_id` |
| `list_channels` | List channels the user follows | `instance_id` |
| `join_channel` | Join a channel | `instance_id`, `channel_id` |
| `leave_channel` | Leave a channel | `instance_id`, `channel_id` |
| `create_instance` | Create a new Telegram instance | `name` |
| `list_instances` | List all instances | — |
| `get_instance_status` | Get status of a specific instance | `instance_id` |
| `send_auth_code` | Send login code to a phone number | `instance_id`, `phone_number` |
| `verify_auth_code` | Verify the received login code | `instance_id`, `code` |
| `submit_2fa` | Submit 2FA password | `instance_id`, `password` |
| `connect_instance` | Connect an authenticated instance | `instance_id` |
| `configure_webhook` | Set webhook URL for an instance | `instance_id`, `url` |
| `test_webhook` | Test webhook delivery | `instance_id` |
| `search_messages` | Search messages in a chat | `instance_id`, `chat_id`, `query`, `limit` |

### MCP Resources

| Resource URI | Description |
|--------------|-------------|
| `telegram://instances` | List of all instances with status |
| `telegram://instances/{id}` | Details of a specific instance |
| `telegram://chats` | Recent chats |
| `telegram://chats/{id}` | Chat details |
| `telegram://contacts` | Contact list |
| `telegram://messages/{chat_id}` | Messages in a specific chat |

### MCP Prompts

| Prompt Name | Description | Arguments |
|-------------|-------------|-----------|
| `compose_message` | Help compose a message for a specific context | `recipient`, `context`, `tone` |
| `summarize_chat` | Summarize recent activity in a chat | `chat_id`, `hours` |
| `draft_reply` | Draft a reply to a specific message | `chat_id`, `message_id` |

### Key Entities

- **MCPServer**: The MCP server instance. Fields: transport (stdio/sse), api_key, tools[], resources[], prompts[].
- **MCPTool**: A registered tool. Fields: name, description, input_schema (JSON Schema), handler function.
- **MCPResource**: A readable resource. Fields: uri_template, name, description, mime_type, handler function.
- **MCPPrompt**: A pre-built prompt template. Fields: name, description, arguments[], template.

## Success Criteria *(mandatory)*

- **SC-001**: An AI agent connected via MCP can send a message to a Telegram contact within 3 tool calls.
- **SC-002**: All 28 tools are discoverable and callable from any MCP-compatible client.
- **SC-003**: Resources are readable and return properly formatted data (JSON).
- **SC-004**: Error messages from the Telegram API are translated into user-friendly MCP responses.
- **SC-005**: The MCP server can run alongside the existing HTTP API without conflicts.
- **SC-006**: Configuration is simple: a single `mcp.json` file or environment variables.

## Assumptions

- The MCP Python SDK (`mcp`) is used as the foundation.
- stdio transport is the primary target (Claude Desktop, Cursor, VS Code).
- SSE transport is secondary for remote deployments.
- The MCP server shares the same database and Redis connections as the HTTP API.
- API key authentication is reused from the existing security layer.
- The MCP server is a separate entry point (`uvicorn app.mcp:app` or `python -m app.mcp`).
- Media downloads return URLs rather than base64-encoded content (to avoid large payloads).
- Rate limits and FloodWait errors are handled the same way as the HTTP API.
- The MCP server does not replace the HTTP API — it complements it.
