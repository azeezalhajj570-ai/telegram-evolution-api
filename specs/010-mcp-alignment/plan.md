# Implementation Plan: MCP Alignment — Response Standardization

**Branch**: `010-mcp-alignment` | **Date**: 2026-05-21 | **Spec**: `specs/010-mcp-alignment/`

**Input**: Audit of `telegram-evolution-api` vs `mcp-evolution-api` standards — response contract, middleware, error codes, sanitization, tool wrappers, REST/MCP unification.

## Summary

Align the Telegram MCP server with the same response contract, middleware pipeline, error code system, sanitization, and tool wrapper architecture established in the Evolution API MCP project. This eliminates architectural drift between the two projects and makes both surfaces predictable for AI clients, SDK generation, and future SaaS features.

## Project Metadata

**Repository**: `relaystack-api` (Python 3.10+, FastAPI + FastMCP)
**Current version**: `0.1.0`
**Target version**: `0.2.0`
**Target Python**: `>=3.10`

## Technical Context

| Aspect | Current | Target |
|--------|---------|--------|
| Response shape | Raw Pydantic models / dicts | `{ success, data, metadata: { requestId, timestamp, version } }` |
| Error format | `{"detail": "..."}` or `{"error": "..."}` | `{ success: false, code, message, retryable, details? }` |
| Middleware | None (auth via DI) | Pipeline: requestContext → logging → rateLimit → auth → response |
| Error codes | JSON-RPC style (-32000 to -32603) | `ErrorCodes` enum with standard codes |
| Tool wrapper | Manual try/except per tool | `create_handler(tool_name, fn)` |
| Sanitization | Full Telegram objects returned | Trimmed to 5-7 essential fields |
| REST ↔ MCP | Different formats | Shared `response.py` contract |

## Deliverables

```text
specs/010-mcp-alignment/
├── plan.md           # This file
└── tasks.md          # Task breakdown

app/
├── core/                          # NEW — shared foundation
│   ├── __init__.py
│   ├── response.py                # success() / error() helpers
│   └── error_codes.py             # ErrorCodes enum
│
├── schemas/
│   └── response.py                # NEW — SuccessResponse, ErrorResponse Pydantic models
│
├── middleware/                     # NEW — middleware pipeline
│   ├── __init__.py
│   ├── compose.py
│   ├── request_context.py
│   ├── logging.py
│   ├── rate_limit.py
│   ├── auth.py
│   └── response.py
│
├── mcp/
│   ├── handler.py                 # NEW — create_handler() wrapper
│   └── sanitize.py                # NEW — sanitize_message/chat/contact/group
│
├── api/                           # MODIFY — REST endpoints use standardized responses
├── mcp/tools/*.py                 # MODIFY — 28 tools use create_handler
└── main.py                        # MODIFY — register middleware
```

## Execution Order

```text
Phase 1 — Response Foundation
    ↓
Phase 2 — Tool Wrapper
    ↓
Phase 3 — Sanitization
    ↓
Phase 4 — Middleware Pipeline
    ↓
Phase 5 — REST + MCP Unification
    ↓
Phase 6 — JWT + Tenant Foundation
```

## Timeline

| Phase | Effort | Files Added | Files Modified |
|-------|--------|-------------|----------------|
| 1 — Response Foundation | Low | 4 | 0 |
| 2 — Tool Wrapper | Low | 1 | 9 |
| 3 — Sanitization | Low | 1 | 7 |
| 4 — Middleware Pipeline | Medium | 7 | 2 |
| 5 — REST Unification | Medium | 0 | 9 |
| 6 — JWT/Tenant | Medium | 3 | 3 |

**Total**: ~16 new files, ~30 modified files
**Estimate**: 6-10 hours across all phases
