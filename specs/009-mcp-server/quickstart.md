# Quickstart: MCP Server

## Prerequisites

- Python 3.10+ (MCP SDK requires 3.10+)
- Running RelayStack API instance (PostgreSQL + Redis)
- API key for authentication
- MCP-compatible client (Claude Desktop, Cursor, VS Code, n8n, etc.)

## Installation

```bash
# Install full dev environment
pip install -e ".[dev]"
```

## Running

### Stdio Transport (for local AI clients)

```bash
python3.11 -m app.mcp
```

This starts the MCP server on stdin/stdout. It reads the same `.env` file as the HTTP API.

### SSE Transport (for remote clients via Docker)

```bash
uvicorn app.mcp.sse:sse_app --host 0.0.0.0 --port 8001
```

## Docker Compose (Production)

```yaml
services:
  app:
    # existing HTTP API service
  mcp-sse:
    build: .
    ports:
      - "127.0.0.1:3011:8001"
    env_file: .env
    command: ["uvicorn", "app.mcp.sse:sse_app", "--host", "0.0.0.0", "--port", "8001"]
```

## Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "relaystack": {
      "command": "python3.11",
      "args": ["-m", "app.mcp"],
      "env": {
        "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/telegram_gateway",
        "API_KEYS": "your-api-key",
        "MCP_API_KEY": "your-mcp-api-key",
        "TELEGRAM_API_ID": "123456",
        "TELEGRAM_API_HASH": "your-api-hash"
      }
    }
  }
}
```

## n8n MCP Node Configuration

```
URL: https://tele.dev.hamedco.com/sse
Transport: SSE
Headers:
  X-API-Key: <global-or-instance-api-key>
  X-Instance-Id: <optional-instance-uuid>
```

## Authentication

Two API key modes:

| Mode | Key Source | Scope |
|------|-----------|-------|
| **Global** | `API_KEYS` env var | Access all instances (must pass `instance_id` in tools) |
| **Instance-scoped** | Generated via `set_instance_api_key` tool | Auto-scoped to one instance |

Headers: `X-API-Key`, `Authorization: Bearer <key>`, or `api_key` query param.

## Verify Setup

```bash
# Health check
curl https://tele.dev.hamedco.com/health

# SSE stream (returns session endpoint)
curl -H "X-API-Key: your-key" https://tele.dev.hamedco.com/sse
```

## Tests

```bash
python3.11 -m pytest tests/test_mcp/ -v
```
