# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of RelayStack API seriously. If you discover a security vulnerability, please follow these steps:

1. **DO NOT** open a public GitHub issue
2. Email us at azeezalhajj570@gmail.com with details about the vulnerability
3. Include steps to reproduce, potential impact, and any suggested fixes
4. We will acknowledge receipt within 48 hours
5. We will provide a detailed response within 7 days
6. We will work on a fix and coordinate disclosure

## Security Best Practices

### For Users

- **Never commit `.env` files** — Always add `.env` to `.gitignore`
- **Use strong API keys** — Generate with `secrets.token_urlsafe(32)` or longer
- **Rotate encryption keys carefully** — Losing `ENCRYPTION_KEY` makes all sessions unrecoverable
- **Use HTTPS in production** — Never expose the API over plain HTTP
- **Restrict network access** — Use firewalls to limit who can reach the API
- **Keep dependencies updated** — Regularly run `pip install --upgrade -e ".[dev]"`
- **Monitor logs** — Set up alerting for suspicious activity patterns

### For Contributors

- **Never log sensitive data** — OTP codes, 2FA passwords, session strings, and API keys must never appear in logs
- **Validate all inputs** — Use Pydantic models for request validation
- **Use parameterized queries** — Never concatenate SQL strings
- **Hash before storage** — API keys must be hashed with bcrypt before database storage
- **Encrypt at rest** — Session strings must be encrypted using Fernet
- **Sign webhooks** — All webhook payloads must include HMAC-SHA256 signatures

## Security Features

### Session Encryption

Telethon session strings are encrypted using Fernet (symmetric encryption) before storage in PostgreSQL. The encryption key is derived from the `ENCRYPTION_KEY` environment variable.

### API Key Security

API keys are:
- Hashed using bcrypt before storage
- Compared using constant-time comparison to prevent timing attacks
- Scoped to specific permissions (organizations feature)

### Webhook Signing

Webhook payloads are signed with HMAC-SHA256 using a per-instance secret. Recipients can verify the signature using the `X-Webhook-Signature` header.

### Rate Limiting

- Per-instance rate limits prevent abuse
- Telegram's FloodWait errors are respected and propagated
- Redis-backed counters ensure consistency across restarts

## Known Security Considerations

- **Telegram account bans**: Automated behavior may trigger Telegram's anti-spam systems. Use dedicated accounts, not your primary Telegram account.
- **Session hijacking**: If an attacker gains access to the database AND the encryption key, they could decrypt session strings. Protect both carefully.
- **Webhook replay attacks**: Webhook signatures include timestamps. Recipients should reject payloads older than a reasonable window (e.g., 5 minutes).

## Dependency Security

We monitor dependencies for known vulnerabilities:

- All dependencies are pinned to minimum versions
- Security updates are prioritized in releases
- Run `pip audit` regularly to check for known vulnerabilities

## Contact

For security concerns, contact: azeezalhajj570@gmail.com
