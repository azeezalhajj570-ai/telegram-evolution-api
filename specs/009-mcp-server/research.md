# Research: MCP Server — Technology Decisions

**Phase 0 Output** — MCP SDK evaluation, transport strategy, and architecture decisions.

## MCP Python SDK

| Decision | Rationale |
|----------|-----------|
| **`mcp` SDK >=1.0.0** | Official Python SDK from the MCP specification authors. Provides `FastMCP` class with decorator-based tool/resource/prompt registration, stdio and SSE transport built-in, JSON Schema auto-generation from Python type hints, and async support. |

### Key SDK API Surface

| API | Purpose |
|-----|---------|
| `FastMCP(name, instructions)` | Main application class. Registers tools, resources, and prompts. |
| `@mcp.tool()` | Decorator that registers a function as an MCP tool. Type-annotated parameters become JSON Schema. |
| `@mcp.resource(uri)` | Decorator that registers a resource handler for the given URI template. |
| `@mcp.prompt()` | Decorator that registers a prompt template with arguments. |
| `mcp.run(transport="stdio")` | Runs the server with stdio transport (stdin/stdout JSON-RPC). |
| `mcp.run_sse()` | Runs the server with SSE transport over HTTP. |

### Alternatives Considered

| Alternative | Reason Against |
|-------------|----------------|
| **Manual JSON-RPC implementation** | No protocol compliance guarantees, reinventing the wheel, no auto-schema generation. |
| **`mcp-server` contrib packages** | Too opinionated, not designed for custom API integration. |
| **Node.js MCP SDK** | Would require separate runtime — not compatible with Python codebase. |

## Transport Strategy

| Decision | Rationale |
|----------|-----------|
| **Stdio transport (primary)** | Required by Claude Desktop, Cursor, VS Code, and most local AI agents. No network overhead, process-based isolation. |
| **SSE transport (secondary)** | Required for remote deployments where the MCP server runs on a different machine than the AI client. Uses existing httpx dependency. |

### Transport Comparison

| Aspect | Stdio | SSE |
|--------|-------|-----|
| Latency | ~1ms (same process) | ~5-50ms (network) |
| Setup | `pip install && python -m app.mcp` | Docker + exposed port |
| Clients | Claude Desktop, Cursor, VS Code | Custom clients, remote agents |
| Auth | Config-based (API key in config) | Per-request header auth |
| Concurrent clients | 1 (one process) | Many (HTTP server) |
| Restart behavior | Process-level | Connection-level |

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **Same-process integration** | MCP server shares the same Python process as the HTTP API. Reuses `TelegramClientManager` singleton, DB engine, Redis connection, and config. Avoids duplication of services and connection pools. |
| **Separate entry point** | MCP runs as `python -m app.mcp` or via a separate uvicorn instance for SSE. Keeps concerns cleanly separated while sharing the codebase. |
| **Decorator-based tool registration** | `@mcp.tool()` decorator on thin wrappers around existing service functions. Each tool is a simple function that calls an existing `app.services.*` method and maps errors. |
| **Config-based API key auth** | For stdio transport, the API key is passed via environment variable or config file (not per-request headers). For SSE, API key is verified on each JSON-RPC request via `X-API-Key` header or `_api_key` parameter. |
| **No new database tables** | MCP is a pure protocol layer. All data is fetched through existing services and repositories. No MCP-specific persistence needed. |
| **Error mapping layer** | A dedicated `errors.py` maps Telegram `RPCError` subclasses and `FloodWaitError` to user-friendly MCP error responses with appropriate error codes. |

### Service Reuse

| HTTP API Service | MCP Tool(s) |
|-----------------|-------------|
| `messaging.send_message()` | `send_message`, `reply_message`, `forward_message` |
| `chats.list_chats()` | `list_chats`, `get_chat_info` |
| `telegram_auth.send_code()` | `send_auth_code` |
| `telegram_auth.verify_code()` | `verify_auth_code` |
| `telegram_auth.submit_2fa()` | `submit_2fa` |
| Instance CRUD (via repository) | `create_instance`, `list_instances`, `get_instance_status` |

## Testing Strategy

| Layer | Tool | Scope |
|-------|------|-------|
| Unit | pytest | Individual tool functions, input validation, error mapping |
| Integration | pytest + mocked Telethon | Tool calls with mocked client, protocol compliance (JSON-RPC) |
| Transport | pytest + subprocess | Stdio server launch and protocol handshake |
| E2E | pytest + httpx (SSE) | Full tool call lifecycle over SSE transport |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `mcp` | >=1.0.0,<2.0.0 | MCP SDK for Python — FastMCP, tool/resource/prompt decorators, stdio + SSE transport |
| `httpx` | >=0.27.0 | Already present — reused for SSE server transport |

**No additional runtime dependencies beyond `mcp`**.

## Deployment

| Mode | Command |
|------|---------|
| Stdio (dev) | `python -m app.mcp` |
| Stdio (Claude Desktop) | `"command": "python", "args": ["-m", "app.mcp"]` in `claude_desktop_config.json` |
| SSE (Docker) | `uvicorn app.mcp.sse:app --host 0.0.0.0 --port 8001` alongside existing API |

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "relaystack": {
      "command": "python",
      "args": ["-m", "app.mcp"],
      "env": {
        "DATABASE_URL": "postgresql+asyncpg://...",
        "API_KEYS": "your-api-key"
      }
    }
  }
}
```
