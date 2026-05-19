# Implementation Plan: MCP Server

**Branch**: `009-mcp-server` | **Date**: 2026-05-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/009-mcp-server/spec.md`

## Summary

Add Model Context Protocol (MCP) server support so AI agents (Claude Desktop, Cursor, etc.) can interact with RelayStack API natively through tools, resources, and prompts. The MCP server wraps existing Telegram API functionality (messaging, chats, contacts, instance management, webhooks) as MCP tools with JSON Schema parameters, exposes Telegram data as MCP resources, and provides pre-built prompt templates for common workflows.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: `mcp` (MCP Python SDK >=1.0.0), FastAPI (existing), Telethon (existing), SQLAlchemy 2.x async (existing), httpx (existing)

**New Dependencies**: `mcp>=1.0.0` (MCP SDK), `httpx` (already present for webhook delivery, reused for SSE)

**Storage**: Same PostgreSQL + Redis as existing API (no new storage)

**Transport**: stdio (primary — Claude Desktop, Cursor, VS Code), SSE (secondary — remote deployments)

**Target Platform**: Linux (Docker Compose deployment, sidecar alongside existing app)

**Performance Goals**: <500ms tool call overhead (MCP SDK + auth, excluding Telegram network), <5s cold start (import + register tools), concurrent tool calls from multiple AI agents

**Constraints**: No new database tables (MCP is a pure protocol layer over existing API), must share DB + Redis connections with HTTP API, must not interfere with HTTP API performance, must reuse existing API key authentication

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Code Quality** ✅
- Pydantic v2 schemas for all tool input/output validation (reused from existing schemas)
- MCP SDK auto-generates tool schemas from type hints → documentation follows
- Structured error responses with user-friendly messages (mapped from Telegram RPC errors)
- Consistent tool naming convention: `snake_case` verbs with domain prefix

**II. Testing Standards** ✅
- Unit tests: tool registration, input validation, error mapping
- Integration tests: tool calls against mocked Telethon (reuse existing fixtures)
- Transport tests: stdio and SSE protocol compliance
- Red-green-refactor: write failing test first for each tool

**III. User Experience Consistency** ✅
- All tools follow MCP protocol conventions (name, description, inputSchema)
- Consistent tool naming: `verb_noun` pattern (e.g., `send_message`, `list_chats`)
- Standard MCP error codes and messages (invalid_params, method_not_found, internal_error)
- Resources use `telegram://` URI scheme for discoverability

**IV. Performance Requirements** ✅
- Tools are registered once at startup (no per-call registration overhead)
- Reuse existing TelegramClientManager client pool (no new Telethon connections)
- Async I/O throughout (MCP native async + existing async stack)
- SSE transport uses single persistent connection per client

**V. Security & Observability** ✅
- API key authentication reused for tool calls (passed via MCP auth or config)
- No new secrets or credentials (reuses existing API key infrastructure)
- Structured logging with correlation IDs (existing logger, no sensitive data)
- Tool call auditing via existing database models

**GATE RESULT**: PASS ✅ — No violations. All principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/009-mcp-server/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 — technology decisions
├── data-model.md        # Phase 1 — MCP entities, tool schemas, resource URIs
├── quickstart.md        # Phase 1 — setup & run guide
├── contracts/           # Phase 1 — MCP tool contracts
│   ├── tools.md         # Tool definitions with JSON Schema
│   ├── resources.md     # Resource URI templates
│   └── prompts.md       # Prompt templates
└── tasks.md             # Phase 2 — implementation tasks
```

### Source Code (repository root)

```text
app/
├── mcp/
│   ├── __init__.py
│   ├── server.py            # MCP server entry: FastMCP app, startup, capability advertisement
│   ├── auth.py               # API key authentication middleware for MCP
│   ├── tools/                # Tool registrations (one file per domain)
│   │   ├── __init__.py
│   │   ├── messaging.py      # send_message, send_media, get_messages, reply, forward, edit, delete, add_reaction
│   │   ├── chats.py          # list_chats, get_chat_info, search_messages
│   │   ├── contacts.py       # list_contacts, import_contact, delete_contact
│   │   ├── groups.py         # list_groups, create_group, add_group_member, remove_group_member
│   │   ├── channels.py       # list_channels, join_channel, leave_channel
│   │   ├── instances.py      # create_instance, list_instances, get_instance_status, connect/disconnect
│   │   └── webhooks.py       # configure_webhook, test_webhook
│   ├── resources/            # Resource handlers
│   │   ├── __init__.py
│   │   ├── instances.py      # telegram://instances, telegram://instances/{id}
│   │   ├── chats.py          # telegram://chats, telegram://chats/{id}
│   │   ├── contacts.py       # telegram://contacts
│   │   └── messages.py       # telegram://messages/{chat_id}
│   ├── prompts/              # Prompt templates
│   │   ├── __init__.py
│   │   └── templates.py      # compose_message, summarize_chat, draft_reply
│   └── errors.py             # Error mapping: Telegram RPC → MCP error codes
```

### Transport Entry Points

```text
# stdio transport (primary — Claude Desktop, Cursor)
app/mcp/__main__.py      # if __name__ == "__main__": mcp.run(transport="stdio")

# SSE transport (secondary — remote deployments)
app/mcp/sse.py           # uvicorn entry point wrapping MCP SSE app
```

## Complexity Tracking

No Constitution violations found. No complexity justification required.

## Phase 0 — Research

**Purpose**: Confirm MCP SDK choice, transport strategy, and integration architecture.

**Findings documented in**: `research.md`

**Key unknowns to resolve**:
1. MCP Python SDK v1.0 API surface — `FastMCP` class, tool decorator, resource decorator, prompt decorator
2. Stdio vs SSE trade-offs for deployment
3. Sharing database sessions and Telethon client pool with the existing HTTP API
4. API key authentication strategy for MCP (config-based vs per-request)
5. Running MCP server alongside existing FastAPI app (same process vs separate)

## Phase 1 — Design & Contracts

**Prerequisites**: research.md complete.

**Generated artifacts**:
1. `data-model.md` — MCP entity definitions, tool signatures, resource URIs, prompt templates
2. `contracts/` — MCP tool catalogs with JSON Schema inputs and outputs, resource URI specs, prompt argument definitions
3. `quickstart.md` — Local dev setup, run, test instructions
4. `AGENTS.md` — Agent context update (plan reference between SPECKIT markers)
