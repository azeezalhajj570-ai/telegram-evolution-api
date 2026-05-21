---

description: "Task list for aligning Telegram MCP server with Evolution MCP response contract, middleware, error codes, sanitization, and tool wrapper standards."

---

# Tasks: MCP Alignment

**Input**: Plan from `specs/010-mcp-alignment/plan.md`

**Format**: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

---

## Phase 1 — Response Foundation

**Purpose**: Shared types and helpers that everything else depends on

- [ ] T001 Create `app/schemas/response.py` — define `SuccessResponse[T]` (Generic Pydantic model) and `ErrorResponse`:

  ```python
  class SuccessResponse(BaseModel, Generic[T]):
      success: Literal[True] = True
      data: T
      metadata: Metadata

  class ErrorResponse(BaseModel):
      success: Literal[False] = False
      code: str
      message: str
      retryable: bool = False
      details: Any = None
      metadata: Metadata

  class Metadata(BaseModel):
      requestId: str
      timestamp: str
      tool: str = ""
      version: str = "0.2.0"
  ```

- [ ] T002 Create `app/core/__init__.py` — package init

- [ ] T003 Create `app/core/error_codes.py` — standard error codes enum:

  ```python
  class ErrorCodes(str, Enum):
      INVALID_INPUT = "INVALID_INPUT"
      NOT_FOUND = "NOT_FOUND"
      AUTH_REQUIRED = "AUTH_REQUIRED"
      RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
      TELEGRAM_API_ERROR = "TELEGRAM_API_ERROR"
      INTERNAL_ERROR = "INTERNAL_ERROR"
  ```

  Map current Telegram RPC error codes:
  | Current JSON-RPC code | New ErrorCodes value |
  |---|---|
  | -32000 (FloodWait) | `RATE_LIMIT_EXCEEDED` |
  | -32001 (RpcCallFail) | `TELEGRAM_API_ERROR` |
  | -32002 (ChatIdInvalid) | `NOT_FOUND` |
  | -32003 (MessageIdInvalid) | `NOT_FOUND` |
  | -32004 (AuthKeyUnregistered) | `AUTH_REQUIRED` |
  | -32005 (PhoneCodeInvalid) | `INVALID_INPUT` |
  | -32006 (SessionPasswordNeeded) | `AUTH_REQUIRED` |
  | -32007 (PhoneNumberBanned) | `AUTH_REQUIRED` |
  | -32008 (Not connected) | `AUTH_REQUIRED` |
  | -32602 (ValueError) | `INVALID_INPUT` |
  | -32099 (Unmapped RPCError) | `TELEGRAM_API_ERROR` |
  | -32603 (Unexpected) | `INTERNAL_ERROR` |

- [ ] T004 Create `app/core/response.py` — `success()` and `error()` helpers:

  ```python
  import uuid, datetime

  VERSION = "0.2.0"

  def _metadata(tool: str = "") -> Metadata:
      return Metadata(
          requestId=str(uuid.uuid4()),
          timestamp=datetime.now(timezone.utc).isoformat(),
          tool=tool,
          version=VERSION,
      )

  def success_tool(tool: str, data: Any, duration_ms: int | None = None) -> SuccessResponse:
      m = _metadata(tool)
      if duration_ms is not None:
          m.durationMs = duration_ms
      return SuccessResponse(data=data, metadata=m)

  def error_tool(tool: str, code: str, message: str, retryable: bool = False, details: Any = None) -> ErrorResponse:
      return ErrorResponse(code=code, message=message, retryable=retryable, details=details, metadata=_metadata(tool))
  ```

**Checkpoint**: `app/schemas/response.py`, `app/core/error_codes.py`, `app/core/response.py` exist and are importable. `success_tool()` and `error_tool()` produce correct shapes.

---

## Phase 2 — Tool Wrapper

**Purpose**: Remove try/except boilerplate from all 28 MCP tools

- [ ] T005 Create `app/mcp/handler.py` — `create_handler()`:

  ```python
  import time
  from app.core.response import success_tool, error_tool
  from app.core.error_codes import ErrorCodes
  from app.mcp.errors import mcp_error_from_telegram

  def create_handler(tool_name: str, fn):
      async def wrapped(**kwargs):
          start = time.monotonic()
          try:
              result = await fn(**kwargs)
              duration = int((time.monotonic() - start) * 1000)
              return success_tool(tool_name, result, duration)
          except Exception as e:
              duration = int((time.monotonic() - start) * 1000)
              err = mcp_error_from_telegram(e)
              # Map JSON-RPC code to ErrorCodes
              code_map = {-32000: ErrorCodes.RATE_LIMIT_EXCEEDED, -32002: ErrorCodes.NOT_FOUND, ...}
              mapped = code_map.get(err["code"], ErrorCodes.TELEGRAM_API_ERROR)
              return error_tool(tool_name, mapped, err["message"], retryable=err["code"] in (-32000, -32001))
      return wrapped
  ```

- [ ] T006 [P] Refactor `app/mcp/tools/messaging.py` — replace try/except in all 8 tools with `create_handler()`:

  | Tool ID | Current pattern | Target |
  |---|---|---|
  | `send_message` | try/except + `_require_instance_id` + manual ret | `create_handler("send_message", handler_fn)` |
  | `send_media` | same | same |
  | `get_messages` | same | same |
  | `reply_message` | same | same |
  | `forward_message` | same | same |
  | `edit_message` | same | same |
  | `delete_message` | same | same |
  | `add_reaction` | same | same |

- [ ] T007 [P] Refactor `app/mcp/tools/chats.py` — 3 tools use `create_handler`

- [ ] T008 [P] Refactor `app/mcp/tools/contacts.py` — 3 tools use `create_handler`

- [ ] T009 [P] Refactor `app/mcp/tools/groups.py` — 4 tools use `create_handler`

- [ ] T010 [P] Refactor `app/mcp/tools/channels.py` — 3 tools use `create_handler`

- [ ] T011 [P] Refactor `app/mcp/tools/instances.py` — 9 tools use `create_handler`

- [ ] T012 [P] Refactor `app/mcp/tools/webhooks.py` — 2 tools use `create_handler`

**Checkpoint**: All 28 tools wrapped in `create_handler()`. No tool file contains `try/except ValueError` or `mcp_error_from_telegram()` directly. Responses are `SuccessResponse` / `ErrorResponse` objects.

---

## Phase 3 — Sanitization

**Purpose**: Trim Telegram response payloads to essential fields to reduce token usage

- [ ] T013 Create `app/mcp/sanitize.py`:

  Function | Input | Output
  ---|---|---
  `sanitize_message(msg: dict) -> dict` | Full Telethon message dict | `{ id, text, type, from, timestamp, has_media? }`
  `sanitize_chat(chat: dict) -> dict` | Full chat dict | `{ id, title, type, unread_count, last_message? }`
  `sanitize_contact(contact: dict) -> dict` | Full contact dict | `{ id, first_name, last_name, phone, username? }`
  `sanitize_group(group: dict) -> dict` | Full group dict | `{ id, title, participants_count, type }`

  Telegram message type mapping:
  | `msg.type` or detection | Output `type` | Output `text` |
  |---|---|---|
  | `Message` with text | `"text"` | `msg.text` |
  | `MessageMediaPhoto` | `"photo"` | caption or `"🖼️ Photo"` |
  | `MessageMediaDocument` | `"document"` | caption or `"📄 Document"` |
  | `MessageMediaWebPage` | `"link"` | `msg.text` or URL |
  | `MessageMediaPoll` | `"poll"` | poll question |
  | `MessageAction` | `"action"` | action description |
  | `MessageService` | `"service"` | service message text |
  | `MessageMediaUnsupported` | `"unsupported"` | `"📨 Unsupported message"` |
  | Grouped media (album) | `"album"` | `"📸 Album (N items)"` |

- [ ] T014 [P] Apply sanitization to `get_messages` tool — wrap output in `[sanitize_message(m) for m in messages]`

- [ ] T015 [P] Apply sanitization to `search_messages` tool — same treatment

- [ ] T016 [P] Apply sanitization to `list_chats` tool — `[sanitize_chat(c) for c in chats]`

- [ ] T017 [P] Apply sanitization to `list_contacts` tool — `[sanitize_contact(c) for c in contacts]`

- [ ] T018 [P] Apply sanitization to `list_groups` / `list_channels` — `[sanitize_group(g) for g in groups]`

**Checkpoint**: All read tools return trimmed payloads. A 30-field Telegram message is now 5-7 fields.

---

## Phase 4 — Middleware Pipeline

**Purpose**: Centralize logging, rate limiting, auth, and response wrapping

- [ ] T019 Create `app/middleware/__init__.py`

- [ ] T020 Create `app/middleware/compose.py` — generic middleware composition:

  ```python
  Middleware = Callable[[RequestContext, Callable], Awaitable[Any]]

  class RequestContext:
      requestId: str = ""
      startTime: float = 0.0
      tool: str = ""
      userId: str = ""
      instanceId: str = ""
      input: Any = None
      response: Any = None

  async def compose(middlewares: list[Middleware], ctx: RequestContext, handler: Callable) -> Any
  ```

- [ ] T021 Create `app/middleware/request_context.py` — generates `ctx.requestId` (uuid4), sets `ctx.startTime`

- [ ] T022 Create `app/middleware/logging.py` — structured log on completion:

  ```python
  print(json.dumps({
      "requestId": ctx.requestId,
      "tool": ctx.tool,
      "duration": (time.monotonic() - ctx.startTime) * 1000,
      "success": ctx.response.get("success") if isinstance(ctx.response, dict) else True
  }))
  ```

- [ ] T023 Create `app/middleware/rate_limit.py` — extract from `app/api/messages.py`, move into pipeline:

  ```python
  key = ctx.instanceId or ctx.userId or "anonymous"
  count = redis.call("INCR", f"ratelimit:{key}")
  if count > 100:
      return error_tool(ctx.tool, ErrorCodes.RATE_LIMIT_EXCEEDED, "Rate limit exceeded", retryable=True)
  ```

- [ ] T024 Create `app/middleware/auth.py` — wraps existing `require_api_key()` into middleware form, sets `ctx.userId`, `ctx.instanceId`

- [ ] T025 Create `app/middleware/response.py` — enriches response metadata from context:

  ```python
  if hasattr(ctx.response, "metadata"):
      ctx.response.metadata.requestId = ctx.requestId
      ctx.response.metadata.durationMs = (time.monotonic() - ctx.startTime) * 1000
  ```

- [ ] T026 Integrate middleware pipeline into `create_handler()` in `app/mcp/handler.py` — compose the pipeline before calling the wrapped handler:

  ```python
  pipeline = compose([
      request_context,
      logging,
      rate_limit,
      auth,
      response,
  ])
  ```

- [ ] T027 Integrate middleware pipeline into FastAPI REST side — create ASGI middleware wrapper that adapts `Request` → `RequestContext` → pipeline → `JSONResponse`

**Checkpoint**: Both MCP tools and REST endpoints run through the same middleware pipeline. Logging, rate limiting, auth, and response enrichment are centralized.

---

## Phase 5 — REST + MCP Unification

**Purpose**: REST endpoints use the same response contract as MCP tools

- [ ] T028 Create `app/api/dependencies.py` — FastAPI `Depends` that returns standardized error responses:

  ```python
  async def get_authenticated_instance(request: Request) -> str:
      key = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
      if not key:
          raise HTTPException(status_code=401, detail=error_tool("", ErrorCodes.AUTH_REQUIRED, "Missing API key").model_dump())
      ...
  ```

- [ ] T029 [P] Refactor `app/api/instances.py` — all endpoints return `SuccessResponse` / `ErrorResponse`:

  | Current | Target |
  |---|---|
  | `{"id": "...", "name": "..."}` | `{"success": true, "data": {"id": "...", "name": "..."}, "metadata": {...}}` |
  | `HTTPException(404, "Instance not found")` | `HTTPException(404, detail=error_tool(...).model_dump())` |

- [ ] T030 [P] Refactor `app/api/auth.py` — same pattern

- [ ] T031 [P] Refactor `app/api/messages.py` — same pattern

- [ ] T032 [P] Refactor `app/api/chats.py` — same pattern

- [ ] T033 [P] Refactor `app/api/webhooks.py` — same pattern

- [ ] T034 [P] Refactor `app/api/organizations.py` — same pattern

- [ ] T035 Update global exception handler in `app/main.py` — return standardized `INTERNAL_ERROR` shape instead of raw `{"error": "internal_error", "detail": "..."}`

- [ ] T036 Remove old error mapping from `app/mcp/errors.py` — integrate into `create_handler()` and `ErrorCodes` instead

**Checkpoint**: REST endpoints return `{ success, data, metadata }` / `{ success: false, code, message }`. HTTP status codes still used (200 for success, 4xx/5xx for errors), but the body follows the contract. The two surfaces (REST + MCP) share response helpers.

---

## Phase 6 — JWT + Tenant Foundation

**Purpose**: Prepare for multi-tenant auth without breaking existing API key auth

- [ ] T037 Create `app/core/jwt.py` — JWT encode/decode with HS256:

  ```python
  def create_token(sub: str, tenant_id: str, role: str, ttl: int = 3600) -> str
  def decode_token(token: str) -> dict | None
  ```

- [ ] T038 Create `app/middleware/jwt_auth.py` — alternative auth middleware that checks `Authorization: Bearer <jwt>` and decodes claims into `ctx`

  | Claim | Context field |
  |---|---|
  | `sub` | `ctx.userId` |
  | `tenant_id` | `ctx.instanceId` (or separate `tenantId`) |
  | `role` | future RBAC |
  | `permissions` | future scope check |

- [ ] T039 Update `app/schemas/response.py` — add optional `tenantId` to `Metadata`:

  ```python
  class Metadata(BaseModel):
      ...
      tenantId: str = ""
  ```

**Checkpoint**: JWT tokens can be issued and verified. The auth middleware accepts both API keys (Phase 4) and JWTs (Phase 6). The `Metadata` carries `tenantId` for future tenant isolation.

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Blocks |
|-------|-----------|--------|
| 1 — Response Foundation | Nothing | All phases |
| 2 — Tool Wrapper | Phase 1 | Phase 4 (middleware integration) |
| 3 — Sanitization | Phase 2 (uses handler pattern) | Nothing |
| 4 — Middleware Pipeline | Phase 1 + Phase 2 | Phase 5, Phase 6 |
| 5 — REST Unification | Phase 4 | Nothing |
| 6 — JWT/Tenant | Phase 4 | Nothing |

### Parallel Opportunities

- **Phase 1**: T001 (schema) and T003 (error codes) can run in parallel
- **Phase 2**: T006 through T012 (all 7 tool files) can run in parallel
- **Phase 3**: T014 through T018 (apply sanitization to read tools) can run in parallel
- **Phase 4**: T021 through T025 (individual middleware modules) can run in parallel
- **Phase 5**: T029 through T034 (all 6 API router files) can run in parallel

---

## Implementation Strategy

1. **Build foundation** (Phase 1): Shared types + helpers — 30 min
2. **Wrap all tools** (Phase 2): `create_handler` — removes 28x duplicated try/except — 1 hour
3. **Trim payloads** (Phase 3): Sanitize read tools — immediate token savings — 30 min
4. **Build middleware** (Phase 4): Centralize logging, rate limiting, auth — 2 hours
5. **Unify REST** (Phase 5): Both surfaces share the contract — 2 hours
6. **JWT foundation** (Phase 6): Future-proof auth — 1 hour

After this phase: every new concern (OpenTelemetry, Redis rate limits, RBAC, SaaS billing) is a new middleware layer — tools never change.
