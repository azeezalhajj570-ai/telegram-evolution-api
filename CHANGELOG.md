# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-tenant SaaS layer with organizations, members, and role-based access control
- Prometheus metrics endpoint (`/metrics`) with request counters, histograms, and gauges
- Structured JSON logging with request ID correlation
- Health (`/health`) and readiness (`/ready`) endpoints
- Admin diagnostics endpoints for instance management and webhook inspection
- Redis-backed async message queue with retry logic and dead-letter handling
- Per-instance and global rate limiting
- Automatic FloodWait error handling with `retry_after_seconds` response
- Idempotency key support for message operations
- Contact management (list, import, delete)
- Group management (create, list, add member, remove member)
- Channel operations (join, leave, list, browse messages)
- Message reactions support
- Media download endpoint
- Webhook delivery retry worker
- HMAC-SHA256 webhook signature verification
- Encrypted session storage using Fernet
- API key hashing with bcrypt
- Startup reconnection for previously authenticated instances

### Changed
- Improved authentication flow with temporary session reuse between `send_code` and `verify_code`
- Updated Docker configuration for standalone deployment

### Fixed
- Resolved `phone_code_hash` mismatch issue during authentication
- Fixed FastAPI route ordering conflicts between specific and wildcard routes
- Cross-database compatibility for JSON columns (SQLite vs PostgreSQL)

## [0.1.0] - 2024-01-01

### Added
- Initial release with core Telegram API gateway functionality
- Instance CRUD operations
- Telegram authentication flow (send code, verify, 2FA, connect)
- Text message sending
- Webhook configuration and delivery
- Chat listing and browsing
- Docker Compose setup with PostgreSQL and Redis
- Basic test suite

[Unreleased]: https://github.com/azeezalhajj570-ai/relaystack-api/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/azeezalhajj570-ai/relaystack-api/releases/tag/v0.1.0
