import time

from prometheus_client import Counter, Gauge, Histogram, generate_latest

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_DURATION = Histogram("http_request_duration_ms", "HTTP request duration ms", ["method", "path"])
ACTIVE_CLIENTS = Gauge("telegram_active_clients", "Currently connected Telethon clients")
QUEUED_JOBS = Gauge("telegram_queued_jobs", "Jobs in message queue")
FAILED_WEBHOOKS = Counter("webhook_delivery_failed_total", "Failed webhook deliveries")
SENT_MESSAGES = Counter("messages_sent_total", "Messages sent via API", ["type"])
FLOOD_WAITS = Counter("telegram_flood_wait_total", "FloodWait pauses triggered")
