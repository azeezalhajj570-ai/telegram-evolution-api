# Contract: Health API

No authentication required.

---

## Health Check

`GET /health`

**Response** `200`:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600,
  "db": "connected",
  "redis": "connected",
  "instances": {
    "total": 5,
    "connected": 3
  }
}
```

**Response** `503` (when DB or Redis is unreachable):
```json
{
  "status": "unhealthy",
  "db": "disconnected",
  "redis": "connected"
}
```
