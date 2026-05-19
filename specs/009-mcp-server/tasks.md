---
description: "Implementation tasks for MCP Server feature"
---

# Tasks: MCP Server

**Input**: Design documents from `/specs/009-mcp-server/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are MANDATORY per the project constitution — every feature MUST include contract, integration, and unit tests where applicable. Tests MUST be written before implementation code (red-green-refactor).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

## Path Conventions

- `app/` at repository root for source code
- `tests/` at repository root for test suite

---

## Phase 1: MCP Foundation (Shared Infrastructure)

**Purpose**: MCP server bootstrap, SDK integration, auth, and transport setup

- [x] T001 Install `mcp` SDK dependency — add `mcp>=1.0.0` to `pyproject.toml` dependencies, run `pip install -e ".[dev]"`, verify import works with `python -c "import mcp; print(mcp.__version__)"`
- [x] T002 [P] Create `app/mcp/__init__.py` — package init with `from app.mcp.server import mcp_app` convenience export
- [x] T003 Create `app/mcp/server.py` — instantiate `FastMCP(name="RelayStack", instructions="...")`, define lifespan that initializes DB engine + Redis + telethon_manager, register all tools/resources/prompts, expose `mcp_app` instance. Add `mcp_app.run()` guard for stdio transport
- [x] T004 [P] Create `app/mcp/__main__.py` — `if __name__ == "__main__":` block that loads `.env`, calls `mcp_app.run(transport="stdio")`. Entry point: `python -m app.mcp`
- [x] T005 [P] Create `app/mcp/auth.py` — API key auth middleware for MCP. For stdio: reads `API_KEYS` from env, stores in-memory. For SSE: FastAPI middleware that validates `X-API-Key` header on each JSON-RPC request, reuses `verify_api_key` from `app.security.api_keys`
- [x] T006 Create `app/mcp/errors.py` — error mapping layer. Map Telegram `RPCError` subclasses to MCP error codes per data-model.md error mapping table. Implement `mcp_error_from_telegram(exception) -> dict` that returns MCP-compatible error response
- [x] T007 [P] Create `app/mcp/sse.py` — FastAPI app wrapping MCP for SSE transport. Instantiate FastAPI, mount `mcp_app` with SSE handler, add health endpoint. Entry point: `uvicorn app.mcp.sse:app`
- [x] T008 [P] Add MCP configuration to `app/config.py` — add `MCP_TRANSPORT: str = "stdio"`, `MCP_HOST: str = "0.0.0.0"`, `MCP_PORT: int = 8001` settings
- [x] T009 [P] Create test directory structure — `tests/test_mcp/__init__.py`, `tests/test_mcp/conftest.py` with fixtures: `mcp_app` fixture, stdio transport fixture, SSE test client fixture, mocked Telethon fixtures (reuse from existing `tests/conftest.py`)

**Checkpoint**: MCP server starts with `python -m app.mcp`, advertises 0 tools (empty registry), accepts stdio JSON-RPC connection

---

## Phase 2: User Story 1 — MCP Server Setup & Tool Discovery (Priority: P1)

**Goal**: MCP server is running, AI clients discover all tools with correct schemas

**Independent Test**: Connect MCP client → request `tools/list` → verify all 28 tools returned with correct names, descriptions, and JSON Schema parameters

### Tests for User Story 1 (MANDATORY) ⚠️

- [x] T010 [P] [US1] Unit test for tool registration discovery — in `tests/test_mcp/test_discovery.py`, test that all 28 tools are registered and `tools/list` returns them with correct names and descriptions
- [x] T011 [P] [US1] Contract test for tool schemas — verify each tool's `inputSchema` has correct required parameters, types, min/max constraints per contracts/tools.md
- [x] T012 [P] [US1] Transport test for stdio — launch MCP server as subprocess with stdio transport, send `tools/list` JSON-RPC, verify response
- [x] T013 [P] [US1] Transport test for SSE — start SSE server with test client, POST JSON-RPC to `/mcp`, verify `tools/list` response
- [x] T014 [US1] Auth test — verify unauthenticated requests return MCP auth error, valid API key succeeds

### Implementation for User Story 1

- [x] T015 [P] [US1] Create base tool registry in `app/mcp/server.py` — implement `_register_all_tools()` that calls all domain tool registration functions
- [x] T016 [P] [US1] Implement `app/mcp/auth.py` `authenticated` wrapper — decorator that verifies API key on each tool call for stdio (env-based) and SSE (header-based). Raise `ValueError` with MCP error code on failure
- [x] T017 [P] [US1] Add lifespan to `app/mcp/server.py` — on startup: create DB engine + session factory, init Redis, import TelegramClientManager, reconnect instances. On shutdown: close all connections. Reuse existing `app.db.database` and `app.services.telegram_manager`

**Checkpoint**: All 28 tools discoverable from any MCP client with correct schemas — server ready for tool implementation

---

## Phase 3: User Story 2 — Core Messaging Tools (Priority: P1)

**Goal**: AI agents can send, read, reply, forward, edit, delete messages, and add reactions

**Independent Test**: Through AI agent: "send hello to @user" → message delivered. "read recent messages" → messages returned. "delete message 123" → message deleted

### Tests for User Story 2 (MANDATORY) ⚠️

- [x] T018 [P] [US2] Unit test for `send_message` tool — in `tests/test_mcp/test_tools_messaging.py`, mock `messaging.send_message`, call tool with valid params, verify correct service call
- [x] T019 [P] [US2] Unit test for `send_media` tool — mock Telethon send_file, call tool, verify
- [x] T020 [P] [US2] Unit test for `get_messages` tool — mock `chats.get_messages`, call tool, verify pagination params
- [x] T021 [P] [US2] Unit test for `reply_message`, `forward_message`, `edit_message`, `delete_message`, `add_reaction` — one test per tool, verify service delegation
- [x] T022 [US2] Integration test — full tool call from MCP JSON-RPC to mocked Telethon response, verify output format matches contract

### Implementation for User Story 2

- [x] T023 [P] [US2] Create `app/mcp/tools/__init__.py` — package init, domain tool registration stubs
- [x] T024 [US2] Create `app/mcp/tools/messaging.py` — implement `register_messaging_tools(mcp)` that registers: `send_message`, `send_media`, `get_messages`, `reply_message`, `forward_message`, `edit_message`, `delete_message`, `add_reaction`. Each tool function calls existing `app.services.messaging` or `app.services.chats` methods and wraps errors via `app.mcp.errors`
- [x] T025 [US2] Wire messaging tools in `app/mcp/server.py` — call `register_messaging_tools(mcp_app)` in `_register_all_tools()`

**Checkpoint**: 8 messaging tools operational — AI agent can fully manage messages through natural language

---

## Phase 4: User Story 3 — Contact & Chat Management Tools (Priority: P2)

**Goal**: AI agents can browse chats, manage contacts, search messages

**Independent Test**: "list my recent chats" → chats returned. "show contacts" → contacts returned. "add contact +5511999999999" → contact imported

### Tests for User Story 3 (MANDATORY) ⚠️

- [x] T026 [P] [US3] Unit tests for chat tools — `list_chats`, `get_chat_info`, `search_messages` in `tests/test_mcp/test_tools_chats.py`
- [x] T027 [P] [US3] Unit tests for contact tools — `list_contacts`, `import_contact`, `delete_contact` in `tests/test_mcp/test_tools_contacts.py`
- [x] T028 [P] [US3] Unit tests for group tools — `list_groups`, `create_group`, `add_group_member`, `remove_group_member` in `tests/test_mcp/test_tools_groups.py`
- [x] T029 [P] [US3] Unit tests for channel tools — `list_channels`, `join_channel`, `leave_channel` in `tests/test_mcp/test_tools_channels.py`

### Implementation for User Story 3

- [x] T030 [P] [US3] Create `app/mcp/tools/chats.py` — implement `register_chat_tools(mcp)` with `list_chats`, `get_chat_info`, `search_messages`. Delegate to existing `app.services.chats`
- [x] T031 [P] [US3] Create `app/mcp/tools/contacts.py` — implement `register_contact_tools(mcp)` with `list_contacts`, `import_contact`, `delete_contact`. Use Telethon `GetContactsRequest`, `ImportContactsRequest`, `DeleteContactsRequest` directly
- [x] T032 [P] [US3] Create `app/mcp/tools/groups.py` — implement `register_group_tools(mcp)` with `list_groups`, `create_group`, `add_group_member`, `remove_group_member`
- [x] T033 [P] [US3] Create `app/mcp/tools/channels.py` — implement `register_channel_tools(mcp)` with `list_channels`, `join_channel`, `leave_channel`
- [x] T034 Wire chat/contact/group/channel tools in server — import and call all four registration functions from `app/mcp/server.py`

**Checkpoint**: 14 additional tools operational (22 total) — AI agent can manage contacts, chats, groups, and channels

---

## Phase 5: User Story 4 — Instance Management Tools (Priority: P2)

**Goal**: AI agents can create, authenticate, and manage Telegram instances

**Independent Test**: "create a new instance" → instance created. "authenticate instance" → auth flow starts. "connect instance" → client connects

### Tests for User Story 4 (MANDATORY) ⚠️

- [x] T035 [P] [US4] Unit tests for instance management tools — `create_instance`, `list_instances`, `get_instance_status` in `tests/test_mcp/test_tools_instances.py`
- [x] T036 [P] [US4] Unit tests for auth flow tools — `send_auth_code`, `verify_auth_code`, `submit_2fa`, `connect_instance` in `tests/test_mcp/test_tools_auth.py`
- [x] T037 [P] [US4] Integration test — full auth flow via MCP tools (create → send_code → verify → connect), mocked Telethon, verify instance status transitions

### Implementation for User Story 4

- [x] T038 [P] [US4] Create `app/mcp/tools/instances.py` — implement `register_instance_tools(mcp)` with `create_instance`, `list_instances`, `get_instance_status`, `send_auth_code`, `verify_auth_code`, `submit_2fa`, `connect_instance`. Delegate to `app.services.telegram_auth` and `app.db.repositories.InstanceRepository`
- [x] T039 [P] [US4] Create `app/mcp/tools/webhooks.py` — implement `register_webhook_tools(mcp)` with `configure_webhook`, `test_webhook`. Delegate to existing webhook services
- [x] T040 Wire instance + webhook tools in server — import and call registration functions from `app/mcp/server.py`

**Checkpoint**: 9 additional tools operational (31 total including webhooks) — full instance lifecycle manageable through AI

---

## Phase 6: MCP Resources (P2)

**Purpose**: Expose Telegram data as readable resources for AI agents

**Independent Test**: Request `telegram://instances` → instances list returned. Request `telegram://chats` → chats returned

### Tests (MANDATORY) ⚠️

- [x] T041 [P] [US3/4] Unit tests for resource handlers — `tests/test_mcp/test_resources.py`, test all 7 resource URIs
- [x] T042 [P] [US4] Test resource content format — verify response has correct `uri`, `mimeType`, `name`, `description`, `text` fields

### Implementation

- [x] T043 [P] Create `app/mcp/resources/__init__.py` — package init
- [x] T044 [P] Create `app/mcp/resources/instances.py` — `register_instance_resources(mcp)` with `telegram://instances` and `telegram://instances/{instance_id}` handlers. Fetch via `InstanceRepository`
- [x] T045 [P] Create `app/mcp/resources/chats.py` — `register_chat_resources(mcp)` with `telegram://chats` and `telegram://chats/{chat_id}` handlers. Fetch via `app.services.chats`
- [x] T046 [P] Create `app/mcp/resources/contacts.py` — `register_contact_resources(mcp)` with `telegram://contacts` handler
- [x] T047 [P] Create `app/mcp/resources/messages.py` — `register_message_resources(mcp)` with `telegram://messages/{chat_id}` and `telegram://messages/{chat_id}/{message_id}` handlers
- [x] T048 Wire all resource registrations in `app/mcp/server.py`

**Checkpoint**: 7 resources operational — AI agents can read Telegram data as structured content

---

## Phase 7: MCP Prompts (P3)

**Purpose**: Provide pre-built interaction templates for common workflows

**Independent Test**: Request prompt `compose_message` with recipient → returns prompt with filled template

### Tests (MANDATORY) ⚠️

- [x] T049 [P] Unit tests for prompts — `tests/test_mcp/test_prompts.py`, test all 3 prompts with valid/invalid arguments

### Implementation

- [x] T050 [P] Create `app/mcp/prompts/__init__.py` — package init
- [x] T051 [P] Create `app/mcp/prompts/templates.py` — `register_prompts(mcp)` with `compose_message`, `summarize_chat`, `draft_reply` using `@mcp.prompt()` decorator. Each returns `Message` list with role and content
- [x] T052 Wire prompts in `app/mcp/server.py`

**Checkpoint**: 3 prompt templates operational — AI agents can use pre-built workflow templates

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, documentation, configuration, testing

- [x] T053 [P] Add comprehensive error handling in `app/mcp/errors.py` — ensure all Telegram RPCError subclasses are mapped, add fallback for unknown errors, test error mapping
- [x] T054 [P] Add logging to all tools — structured logging with tool name, params (no sensitive data), duration, error status. Use existing `logger`
- [x] T055 [P] Add resource caching — cache instance list response for 30s to reduce DB load on repeated reads, use Redis or in-memory TTL cache
- [x] T056 [P] Add response size limits — truncate large message lists to configured max (default 100), return warning in response
- [x] T057 [P] Add SSE transport health checks — `GET /health` returns MCP server status, connected instance count, uptime
- [x] T058 [P] Add stdio process health — heartbeat/ping handler, graceful shutdown on SIGTERM
- [x] T059 [P] Update `README.md` — add MCP server section with configuration examples for Claude Desktop, Cursor, VS Code
- [x] T060 [P] Add MCP environment variables to `.env.example` — `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT`
- [x] T061 [P] Add MCP section to `API_EXAMPLES.md` — curl examples for SSE transport, Claude Desktop config example
- [x] T062 [P] Create `tests/test_mcp/test_transport_sse.py` — full SSE protocol integration test with FastAPI TestClient
- [x] T063 [P] Create `tests/test_mcp/test_transport_stdio.py` — subprocess stdio test, verify JSON-RPC handshake

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundation (Phase 1)**: No dependencies — can start immediately
- **Tool Discovery (Phase 2)**: Depends on Foundation
- **Messaging Tools (Phase 3)**: Depends on Foundation — NO dependency on Phase 2 discovery
- **Contact/Chat Tools (Phase 4)**: Depends on Foundation — NO dependency on Phase 2/3
- **Instance Tools (Phase 5)**: Depends on Foundation — NO dependency on Phase 2/3/4
- **Resources (Phase 6)**: Depends on Foundation — NO dependency on tool phases
- **Prompts (Phase 7)**: Depends on Foundation — NO dependency on tools/resources
- **Polish (Phase 8)**: Depends on all other phases complete

### Within Each Phase

- Tests MUST be written and FAIL before implementation (mandatory per constitution)
- Domain tool registrations can be implemented in any order
- Each tool is independently testable

### Parallel Execution Strategy

All tool domain phases (3, 4, 5) can run IN PARALLEL after Foundation completes:

```
Phase 1: Foundation (T001-T009)
  │
  ├── Phase 2: Discovery (T010-T017) — optional, can merge with any phase
  ├── Phase 3: Messaging tools (T018-T025)
  ├── Phase 4: Contact/Chat tools (T026-T034)
  ├── Phase 5: Instance tools (T035-T040)
  ├── Phase 6: Resources (T041-T048)
  ├── Phase 7: Prompts (T049-T052)
  │
  └── Phase 8: Polish (T053-T063) — after all other phases
```

### Parallel Example: Phase 1 + Phase 2

```bash
Task: "T001 add mcp dependency"
Task: "T005 [P] auth middleware"
Task: "T007 [P] SSE transport"
```

### Parallel Example: Tool Phases (3, 4, 5)

```bash
# All independent — different files, no shared deps:
Task: "T024 [US2] messaging tools"
Task: "T030 [P] [US3] chat tools"
Task: "T031 [P] [US3] contact tools"
Task: "T038 [P] [US4] instance tools"
```

---

## Implementation Strategy

### MVP First (Tools Only)

1. Complete Phase 1: Foundation (T001-T009)
2. Complete Phase 3: Messaging tools (T018-T025) — 8 core tools
3. **STOP and VALIDATE**: AI agent can send/read/manage messages
4. Add Phase 5: Instance tools (T035-T040) — full lifecycle management

### Full Delivery

1. Foundation → all tool phases → resources → prompts → polish

### Parallel Team Strategy

With multiple developers:
1. Developer A: Phase 1 (Foundation) + Phase 2 (Discovery)
2. Developer B: Phase 3 (Messaging tools) + Phase 7 (Prompts)
3. Developer C: Phase 4 (Contact/Chat tools) + Phase 6 (Resources)
4. Developer D: Phase 5 (Instance tools)
5. All: Phase 8 (Polish)

---

## Notes

- 63 total tasks across 8 phases
- 5 user stories (2 P1, 2 P2, 1 P3)
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each tool is independently completable and testable
- Verify tests fail before implementing (red-green-refactor)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
