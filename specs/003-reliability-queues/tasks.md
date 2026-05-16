---
description: "Implementation tasks for Reliability & Queues"
---

# Tasks: Reliability & Queues

## Phase 1: Queue Infrastructure

- [ ] T001 Create `app/services/message_queue.py` — `enqueue(instance_id, job_type, payload, idempotency_key)` pushes JSON to Redis list `queue:{instance_id}`; `dequeue(instance_id)` pops from list
- [ ] T002 Add SendJob status management in `app/services/message_queue.py` — `set_job_status(job_id, status, **fields)`, `get_job(job_id)`, job status states: queued → processing → delivered|failed → dead_letter

## Phase 2: Rate Limiting + FloodWait

- [ ] T003 Rewrite `app/services/rate_limits.py` — add per-instance sliding window (20/60s) + per-user global limit (100/60s); `check_rate_limit(instance_id, user_id) → (allowed, retry_after, remaining)`
- [ ] T004 Add FloodWait pause in `app/services/message_queue.py` — `set_flood_wait(instance_id, seconds)`, `is_paused(instance_id) → bool`

## Phase 3: Message Worker

- [ ] T005 Create `app/workers/message_worker.py` — background loop that iterates active instances, dequeues jobs, checks pause + rate limit, calls `send_message`/`send_media` from messaging service, handles FloodWait by pausing, retries on failure, moves to dead-letter after max retries
- [ ] T006 Wire worker into `app/main.py` lifespan — start as asyncio background task

## Phase 4: API Changes

- [ ] T007 Create `app/schemas/queue.py` — `JobStatusResponse`, `RateLimitResponse`, `SendTextQueuedRequest` (with optional idempotency_key)
- [ ] T008 Create `app/api/queue.py` — `POST /instances/{id}/messages/send-text` (returns 202 + job_id), `GET /instances/{id}/messages/jobs/{job_id}`, `GET /instances/{id}/rate-limit`
- [ ] T009 Modify `app/api/messages.py` — existing send-message now enqueues instead of sending directly

## Phase 5: Idempotency

- [ ] T010 Add idempotency check in `app/services/message_queue.py` — `check_idempotency(key) → job_id or None`, store mapping with 24h TTL
- [ ] T011 Add `POST /instances/{id}/messages/send-media` queue endpoint (replaces direct send)

## Phase 6: Tests

- [ ] T012 Write `tests/test_message_queue.py` — test enqueue, dequeue, job status, idempotency dedup
- [ ] T013 Write `tests/test_rate_limits.py` — test per-instance limit, per-user limit, FloodWait pause
- [ ] T014 Write `tests/test_message_worker.py` — test worker processes job, retries on failure, moves to dead-letter
