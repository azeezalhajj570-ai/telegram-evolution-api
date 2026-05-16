# Feature Specification: Observability + Admin Operations

**Feature Branch**: `006-observability-admin`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "Add observability, monitoring, and admin operations to the Telegram Evolution API: structured logging, metrics, health checks, diagnostics, instance recovery, webhook inspection."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Health & Readiness (Priority: P1)

As a platform operator, I want health and readiness endpoints so that my load balancer and orchestrator can route traffic correctly.

**Why this priority**: Health checks are the foundation of production operations.

**Independent Test**: Can be tested by calling `/health` and `/ready` when all services are up and again when one service (e.g., Redis) is unavailable, verifying the response changes.

**Acceptance Scenarios**:

1. **Given** all services running, **When** I GET `/health`, **Then** the response is 200 with status "healthy" and DB/Redis connectivity.
2. **Given** all services running, **When** I GET `/ready`, **Then** the response is 200 with status "ready".
3. **Given** PostgreSQL is unreachable, **When** I GET `/health`, **Then** the response is 503 with status "unhealthy".
4. **Given** Redis is unreachable, **When** I GET `/ready`, **Then** the response is 503 with status "not_ready".

---

### User Story 2 - Structured Logging & Metrics (Priority: P1)

As a platform operator, I want structured JSON logs and Prometheus-format metrics so that I can monitor system health and debug issues.

**Why this priority**: Observability is essential for operating in production.

**Independent Test**: Can be tested by sending a few API requests, then checking that log entries are valid JSON with correlation IDs and that the `/metrics` endpoint returns Prometheus-format counters.

**Acceptance Scenarios**:

1. **Given** any API request, **When** it is processed, **Then** a structured JSON log entry is emitted with request_id, method, path, status_code, duration_ms, and instance_id (if applicable).
2. **Given** the application is running, **When** I GET `/metrics`, **Then** the response is Prometheus text format with counters for requests, active clients, failed webhooks, queued jobs, sent messages, and FloodWait pauses.
3. **Given** a request with an error, **When** it is logged, **Then** the log entry includes the error message and stack trace (without sensitive data).
4. **Given** any log entry, **When** it is inspected, **Then** no OTP codes, 2FA passwords, API keys, or session strings appear in the output.

---

### User Story 3 - Admin Instance Operations (Priority: P2)

As a platform operator, I want admin APIs to inspect and recover instances so that I can troubleshoot and fix issues without database access.

**Why this priority**: Admin recovery reduces MTTR for production incidents.

**Independent Test**: Can be tested by connecting an instance, then using the diagnostics endpoint to verify its state, and using the restart endpoint to force a reconnect.

**Acceptance Scenarios**:

1. **Given** any instance, **When** a user with admin scope GETs `/admin/instances/{id}/diagnostics`, **Then** the response includes connection status, Telethon client health, active webhook, recent errors, and FloodWait state.
2. **Given** a disconnected instance with a saved session, **When** an admin POSTs to `/admin/instances/{id}/restart`, **Then** the Telethon client is restarted and the instance reconnects.
3. **Given** an instance in "auth_required" status, **When** an admin POSTs restart, **Then** the API returns an error indicating re-authentication is needed.
4. **Given** a non-admin user, **When** they attempt to access admin endpoints, **Then** the API returns a 403 error.

---

### User Story 4 - Webhook Delivery Inspection (Priority: P3)

As a platform operator, I want to inspect and retry webhook deliveries so that I can diagnose integration issues.

**Why this priority**: Webhook inspection is important but secondary to core instance operations.

**Independent Test**: Can be tested by configuring a webhook that returns 500, sending a message to trigger delivery, then inspecting the failed delivery and manually retrying it.

**Acceptance Scenarios**:

1. **Given** webhook deliveries exist, **When** an admin GETs `/admin/webhook-deliveries`, **Then** the response is a paginated list with status, attempt count, last status code, and payload preview.
2. **Given** a failed webhook delivery, **When** an admin POSTs to `/admin/webhook-deliveries/{id}/retry`, **Then** the delivery is re-queued for the worker.
3. **Given** a non-admin user, **When** they attempt to access webhook delivery endpoints, **Then** the API returns a 403 error.

---

### Edge Cases

- What happens when a metrics counter overflows? Prometheus counters wrap naturally; the system uses unsigned 64-bit integers.
- What happens when structured logging encounters a binary field? Binary data is base64-encoded or truncated.
- What happens when an admin restarts an instance that is sending a message? The message is interrupted and retried by the queue worker.
- What happens when the diagnostics endpoint is called for a deleted instance? The API returns a 404 error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a `/health` endpoint that checks PostgreSQL and Redis connectivity.
- **FR-002**: The system MUST expose a `/ready` endpoint that returns 200 only when the application is fully initialized and accepting traffic.
- **FR-003**: The system MUST expose a `/metrics` endpoint in Prometheus text format.
- **FR-004**: The system MUST emit structured JSON logs with request_id, method, path, status, and duration.
- **FR-005**: The system MUST assign a unique request_id to every HTTP request.
- **FR-006**: The system MUST prevent sensitive data (OTP, passwords, API keys, sessions) from appearing in logs.
- **FR-007**: The system MUST expose an admin diagnostics endpoint per instance.
- **FR-088**: The system MUST expose an admin restart endpoint per instance.
- **FR-009**: The system MUST expose admin endpoints for listing and retrying webhook deliveries.
- **FR-010**: The system MUST protect all admin endpoints with an admin API key scope.
- **FR-011**: Metrics MUST include active clients, failed webhooks, queued jobs, sent messages, and FloodWait pauses.

### Key Entities

- **RequestContext**: Transient per-request data including request_id, start_time, instance_id (extracted from route params), and actor_id.
- **MetricCounter**: In-memory counters (Prometheus) for key operational metrics. Not persisted.
- **DiagnosticsReport**: Snapshot of an instance's internal state. Fields: instance_id, status, client_connected, client_healthy, webhook_active, floodwait_paused, floodwait_remaining, last_error, uptime.

## Success Criteria *(mandatory)*

- **SC-001**: `/health` and `/ready` endpoints respond in under 100ms.
- **SC-002**: All API requests produce a structured JSON log entry within 100ms of completion.
- **SC-003**: No sensitive data appears in any log output during normal operation or error scenarios.
- **SC-004**: `/metrics` returns at least 10 metric counters after processing a few requests.
- **SC-005**: Admin diagnostics returns a complete snapshot of instance state in under 500ms.
- **SC-006**: Admin restart successfully reconnects a disconnected instance within 15 seconds.

## Assumptions

- Prometheus is used for metric collection and alerting.
- Logs are collected by a centralized logging system (e.g., Loki, ELK, Datadog).
- Request IDs are UUIDs generated per request.
- Metrics are in-memory only; they reset on application restart.
- Admin endpoints require a separate auth scope (`admin:*`) beyond standard API key scopes.
- Metrics granularity is per-instance for debugging but per-app for operational dashboards.
