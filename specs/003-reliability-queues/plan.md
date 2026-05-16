# Implementation Plan: Reliability & Queues

**Branch**: `003-reliability-queues` | **Date**: 2026-05-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-reliability-queues/spec.md`

## Summary

Move message sending from synchronous API calls to a Redis-backed async queue. Add per-instance rate limits, FloodWait auto-pause, retries with dead-letter, and idempotency keys.

## Technical Context

**Language/Version**: Python 3.9+ (same as MVP)

**Primary Dependencies**: redis (already in deps), arq or custom Redis list-based queue

**Storage**: Redis (queue, rate-limit counters, FloodWait state, idempotency keys, job status), PostgreSQL (delivery logs)

**Testing**: pytest, pytest-asyncio, fakeredis or mock redis, unittest.mock (mocked Telethon)

**Target Platform**: Linux (Docker Compose — Redis already running)

**Project Type**: web-service (extends existing)

**Performance Goals**: <500ms API response (enqueue only); messages delivered within 30s under normal conditions

**Constraints**: No job loss on restart (Redis persistence); max 3 retries with exponential backoff; FloodWait pauses handled automatically

**Scale/Scope**: Single Redis instance, single worker, extends existing codebase

## Constitution Check ✅

All 5 principles satisfied.

## Project Structure — New/Modified Files

```text
app/
├── schemas/
│   └── queue.py               # NEW — job status, rate-limit schemas
├── services/
│   ├── message_queue.py        # NEW — Redis-based enqueue/dequeue
│   └── rate_limits.py          # REWRITE — per-instance + per-user limits
├── workers/
│   └── message_worker.py       # NEW — processes queued messages
├── api/
│   ├── messages.py             # MODIFY — send endpoints return job_id
│   └── queue.py                # NEW — job status, rate-limit endpoints
└── db/
    └── models.py               # MODIFY — add SendJob model
tests/
├── test_message_queue.py       # NEW — queue enqueue/dequeue tests
├── test_message_worker.py      # NEW — worker processing tests
└── test_rate_limits.py         # NEW — rate-limit tests
```
