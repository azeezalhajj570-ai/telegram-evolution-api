# Production Deployment Guide

This guide covers deploying RelayStack API in a production environment.

## Prerequisites

- Docker and Docker Compose
- PostgreSQL 15+ (or use the included Docker service)
- Redis 7+ (or use the included Docker service)
- Telegram API credentials from [my.telegram.org](https://my.telegram.org/apps)
- A domain name with SSL certificate (recommended)

## Quick Deploy

```bash
# Clone and configure
git clone https://github.com/your-org/relaystack-api.git
cd relaystack-api
cp .env.example .env

# Edit .env with your production values
# Then start:
docker compose up -d --build
```

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_API_ID` | Telegram API ID | `12345678` |
| `TELEGRAM_API_HASH` | Telegram API hash | `abcdef1234567890` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql+asyncpg://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection | `redis://host:6379/0` |
| `ENCRYPTION_KEY` | 32-byte hex key for session encryption | `$(python3 -c "import secrets; print(secrets.token_hex(32))")` |
| `API_KEYS` | Comma-separated API keys | `$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `RATE_LIMIT_MAX` | `5` | Max requests per window per instance |
| `RATE_LIMIT_WINDOW` | `60` | Rate limit window in seconds |
| `WEBHOOK_TIMEOUT` | `30` | Webhook delivery timeout in seconds |
| `WEBHOOK_MAX_RETRIES` | `3` | Max webhook retry attempts |

## Telegram Account Safety

- **Use dedicated accounts** — Do not use your primary Telegram account. Create separate accounts for API use.
- **Respect rate limits** — The gateway handles `FloodWaitError` automatically, but your application should respect the `retry_after_seconds` values.
- **Monitor account health** — Check instance status regularly. If status becomes `auth_required`, the session was invalidated.
- **Avoid spam-like behavior** — Space out messages to natural intervals. Rapid messaging triggers Telegram's anti-spam systems.
- **One session per account** — Logging in elsewhere (Telegram app, web) will invalidate the gateway session.

## Reverse Proxy Setup

### Nginx

```nginx
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/ssl/certs/api.example.com.crt;
    ssl_certificate_key /etc/ssl/private/api.example.com.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Caddy

```caddy
api.example.com {
    reverse_proxy localhost:8000
}
```

## Scaling

### Single Server

For 5-20 instances, PostgreSQL and Redis on the same server is sufficient.

### Multiple App Instances

- Sessions are stored encrypted in PostgreSQL, so multiple app instances can share the same database.
- However, Telethon clients are in-memory — each app instance maintains its own client pool.
- For high availability, consider implementing the horizontal scaling features (Phase 7).

### Database Scaling

- Use connection pooling (PgBouncer) for high connection counts
- Enable PostgreSQL WAL archiving for point-in-time recovery
- Consider read replicas for heavy read workloads

### Redis Scaling

- Enable Redis persistence (RDB snapshots or AOF) to preserve queue state across restarts
- Use Redis Sentinel or Cluster for high availability

## Monitoring

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Prometheus metrics
curl http://localhost:8000/metrics
```

### Prometheus Configuration

```yaml
scrape_configs:
  - job_name: 'relaystack-api'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
```

### Key Metrics

- `http_requests_total` — Total HTTP requests by method, path, and status
- `http_request_duration_seconds` — Request duration histogram
- `telegram_instances_total` — Total instances by status
- `telegram_messages_sent_total` — Total messages sent
- `webhook_deliveries_total` — Webhook delivery attempts by status
- `queue_depth` — Current message queue depth

### Logging

Structured JSON logs are recommended for production. Set `LOG_LEVEL=INFO` and use a log aggregator:

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "request_id": "abc-123",
  "method": "POST",
  "path": "/instances/1/send-message",
  "status": 200,
  "duration_ms": 150
}
```

## Backup and Recovery

### Database Backup

```bash
# Backup
pg_dump -U postgres telegram_gateway > backup_$(date +%Y%m%d).sql

# Restore
psql -U postgres telegram_gateway < backup_20240101.sql
```

### Encryption Key Backup

The `ENCRYPTION_KEY` is critical — losing it makes all sessions unrecoverable.

- Store in a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
- Back up securely with restricted access
- Document the recovery procedure

### Recovery Procedure

1. Restore PostgreSQL from backup
2. Ensure `ENCRYPTION_KEY` matches the original
3. Start the application
4. Instances will reconnect automatically on startup

## Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] Strong API keys generated (32+ bytes)
- [ ] `ENCRYPTION_KEY` stored securely
- [ ] `.env` file not committed to version control
- [ ] Firewall rules restrict access to necessary ports
- [ ] Regular dependency updates (`pip audit`)
- [ ] Log monitoring and alerting configured
- [ ] Database backups scheduled and tested
- [ ] Rate limiting configured appropriately

## Troubleshooting

### Instance Won't Connect

- Check Telegram API credentials are correct
- Verify network connectivity to Telegram servers
- Check logs for authentication errors

### Messages Not Sending

- Verify instance status is `connected`
- Check rate limits and FloodWait delays
- Verify Redis is running and accessible

### Webhooks Not Delivering

- Check webhook URL is accessible from the server
- Verify SSL certificate if using HTTPS
- Check webhook delivery logs for errors

### High Memory Usage

- Telethon clients consume memory per instance
- Consider limiting concurrent instances
- Monitor client pool size
