# Quickstart: MCP Server

## Prerequisites

- Python 3.12+
- Running RelayStack API instance (PostgreSQL + Redis)
- API key for authentication
- MCP-compatible client (Claude Desktop, Cursor, VS Code, etc.)

## Installation

```bash
# Install MCP SDK
pip install "mcp>=1.0.0"

# Or install full dev environment
pip install -e ".[dev]"
```

## Running

### Stdio Transport (for local AI clients)

```bash
python -m app.mcp
```

This starts the MCP server on stdin/stdout. It reads the same `.env` file as the HTTP API.

### SSE Transport (for remote clients)

```bash
uvicorn app.mcp.sse:app --host 0.0.0.0 --port 8001
```

## Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "relaystack": {
      "command": "python",
      "args": ["-m", "app.mcp"],
      "env": {
        "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/telegram_gateway",
        "REDIS_URL": "redis://localhost:6379/0",
        "API_KEYS": "your-api-key",
        "TELEGRAM_API_ID": "123456",
        "TELEGRAM_API_HASH": "your-api-hash"
      }
    }
  }
}
```

## Docker Compose (Sidecar)

```yaml
services:
  app:
    # existing HTTP API
  mcp:
    build: .
    command: uvicorn app.mcp.sse:app --host 0.0.0.0 --port 8001
    env_file: .env
    ports:
      - "8001:8001"
    depends_on:
      - postgres
      - redis
```

## Verify Setup

```bash
# Check MCP server is running (SSE)
curl http://localhost:8001/health

# List available tools (via SSE)
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Call a tool
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_instances","arguments":{}}}'
```

## Run Tests

```bash
# All MCP tests
pytest tests/test_mcp/ -v

# Specific domain
pytest tests/test_mcp/test_tools_messaging.py -v

# Transport tests
pytest tests/test_mcp/test_transport_stdio.py -v
pytest tests/test_mcp/test_transport_sse.py -v
```
