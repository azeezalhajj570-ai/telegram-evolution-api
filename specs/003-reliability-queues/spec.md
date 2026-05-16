# Feature Specification: Reliability & Queues

**Feature Branch**: `003-reliability-queues`

**Created**: 2026-05-16

**Status**: Draft

**Input**: User description: "Add production-grade reliability to the Telegram Evolution API: Redis-backed outgoing message queue, retries, rate limiting, dead-letter handling, FloodWait prevention, message status tracking."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Send Via Queue (Priority: P1)

As a developer, I want to send messages without blocking on Telegram's response so that my API calls return instantly and the system handles retries automatically.

**Why this priority**: This is the core reliability feature — it decouples API response time from Telegram network latency.

**Independent Test**: Can be tested by POSTing a send-text request and immediately receiving a `job_id` response, then polling the job status endpoint and confirming the message was eventually delivered.

**Acceptance Scenarios**:

1. **Given** a connected instance, **When** I POST to `/instances/{id}/messages/send-text`, **Then** the response returns immediately with a `job_id` and status "queued".
2. **Given** a queued job, **When** I GET `/instances/{id}/messages/jobs/{job_id}`, **Then** the response shows the current job status (queued, sending, delivered, failed).
3. **Given** an invalid target chat, **When** the worker processes the job, **Then** the job status becomes "failed" with an error description.
4. **Given** a successful send, **When** I poll the job status, **Then** it eventually shows "delivered" with the Telegram message ID.

---

### User Story 2 - FloodWait Resilience (Priority: P1)

As a developer, I want the system to automatically pause sending when Telegram enforces a rate limit so that my application never sees FloodWait errors and the instance recovers without manual intervention.

**Why this priority**: FloodWait is the most common production issue with Telegram APIs. Automated handling is essential for reliability.

**Independent Test**: Can be tested by configuring a very low rate limit, sending messages rapidly until FloodWait triggers, and verifying subsequent sends are queued and processed after the pause period expires.

**Acceptance Scenarios**:

1. **Given** a FloodWait error from Telegram, **When** the worker encounters it, **Then** the instance is paused for the required duration and queued jobs remain pending.
2. **Given** a paused instance, **When** I send another message, **Then** it is accepted into the queue (not rejected) and processed when the pause expires.
3. **Given** the pause period has elapsed, **When** the worker retries the queued job, **Then** it succeeds and normal sending resumes.
4. **Given** a connected instance, **When** I GET `/instances/{id}/rate-limit`, **Then** the response shows current burst tokens, remaining capacity, and any active pause.

---

### User Story 3 - Retry & Dead-Letter Queue (Priority: P2)

As a developer, I want failed message deliveries to be automatically retried and eventually moved to a dead-letter queue so that no messages are silently lost.

**Why this priority**: Data loss prevention is critical for production systems.

**Independent Test**: Can be tested by configuring max_retries=3, sending a message to an invalid chat, and verifying the job is retried 3 times then moved to dead-letter.

**Acceptance Scenarios**:

1. **Given** a failed send, **When** the retry delay expires, **Then** the job is re-attempted.
2. **Given** all retries exhausted, **When** the job fails again, **Then** the job status becomes "dead_letter" and is not retried further.
3. **Given** a message in the dead-letter queue, **When** I request the job status, **Then** it includes the failure reason and attempt history.

---

### User Story 4 - Idempotency (Priority: P2)

As a developer, I want to safely retry API calls without risk of duplicate messages so that I can implement reliable client-side retry logic.

**Why this priority**: Idempotency is a standard reliability pattern that prevents double-sends.

**Independent Test**: Can be tested by sending the same request twice with the same idempotency key and confirming only one message is delivered.

**Acceptance Scenarios**:

1. **Given** a send request with an idempotency key, **When** the same request is sent again, **Then** the second call returns the existing job_id instead of creating a new job.
2. **Given** an idempotent request, **When** the original job is still processing, **Then** the second call returns "processing" status with the same job_id.
3. **Given** an idempotent request, **When** the original job is completed, **Then** the second call returns the completed status.

---

### Edge Cases

- What happens when Redis is down? The queue is unavailable; send endpoints return a 503 error.
- What happens when the message queue grows very large? Redis persists to disk; backpressure is handled by rate limiting.
- What happens when an instance is disconnected mid-queue? Queued jobs remain pending; they resume when the instance reconnects.
- What happens when the application restarts with pending jobs? Jobs are persisted in Redis and picked up on restart.
- What happens when a job exceeds the maximum retry count? It moves to dead-letter status, logged, and no longer retried.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST enqueue outgoing message send requests and return a `job_id` immediately.
- **FR-002**: The system MUST support querying job status by `job_id`.
- **FR-003**: The system MUST implement per-instance rate limiting with configurable max messages per time window.
- **FR-004**: The system MUST implement per-user (global) rate limiting as a safety net.
- **FR-005**: The system MUST automatically retry failed send jobs with exponential backoff.
- **FR-006**: The system MUST move jobs to a dead-letter queue after exhausting max retries.
- **FR-007**: The system MUST detect FloodWait errors and pause the offending instance for the required duration.
- **FR-008**: The system MUST expose current rate-limit state per instance via API.
- **FR-009**: The system MUST support optional idempotency keys on send endpoints.
- **FR-010**: The system MUST track and expose delivery status per job.
- **FR-011**: The system MUST persist the queue in Redis so jobs survive application restart.

### Key Entities

- **SendJob**: A queued outgoing message request. Fields: job_id, instance_id, type (text/media), payload, status (queued/sending/delivered/failed/dead_letter), idempotency_key, attempt_count, max_retries, created_at.
- **RateLimitState**: The current rate-limit status for an instance. Fields: instance_id, remaining_tokens, burst_capacity, is_paused, pause_until, reset_at.
- **DeliveryLog**: A record of each delivery attempt. Fields: job_id, attempt_number, status, error_message, timestamp.

## Success Criteria *(mandatory)*

- **SC-001**: All send endpoints return a `job_id` within 500ms regardless of Telegram latency.
- **SC-002**: A queued message is delivered within 30 seconds under normal conditions.
- **SC-003**: A FloodWait pause of 60 seconds holds all outbound traffic for that instance and automatically resumes.
- **SC-004**: A message to an invalid chat is retried 3 times then moved to dead-letter within 5 minutes.
- **SC-005**: Duplicate requests with the same idempotency key never result in duplicate messages.
- **SC-006**: The system handles 100+ queued jobs per instance without degradation.

## Assumptions

- Redis is available and configured with persistence (RDB/AOF).
- The queue worker runs in-process as an asyncio background task.
- Idempotency keys expire after 24 hours.
- Default max retries is 3 with exponential backoff (60s, 120s, 240s).
- Per-instance rate limit defaults to 20 messages per 60 seconds.
- Per-user (global) rate limit defaults to 100 messages per 60 seconds across all instances.
- FloodWait pause times are read from Telegram's `retry_after` field.
- Job history is retained for 7 days then pruned.
