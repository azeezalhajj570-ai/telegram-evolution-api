import asyncio
import logging
from typing import Dict, Optional

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from app.config import settings
from app.security.encryption import decrypt

logger = logging.getLogger(__name__)


def _build_newmessage_handler(instance_id: str):
    async def handler(event):
        from app.db.database import async_session
        from app.db.repositories import WebhookRepository
        from app.services.webhook_dispatcher import dispatch, normalize_message

        event_data = normalize_message(event)
        async with async_session() as db:
            wh_repo = WebhookRepository(db)
            await dispatch(instance_id, "message", event_data, wh_repo)
            await db.commit()

    return handler


class TelegramClientManager:
    def __init__(self):
        self._clients: Dict[str, TelegramClient] = {}
        self._lock = asyncio.Lock()

    async def start_client(self, instance_id: str, session_encrypted: str) -> TelegramClient:
        async with self._lock:
            existing = self._clients.get(instance_id)
            if existing and existing.is_connected():
                return existing

            session_str = decrypt(session_encrypted, settings.encryption_key.encode())
            client = TelegramClient(StringSession(session_str), settings.telegram_api_id, settings.telegram_api_hash)
            await client.start()

            client.on(events.NewMessage)(_build_newmessage_handler(instance_id))

            self._clients[instance_id] = client
            logger.info("Started Telethon client for instance %s", instance_id)
            return client

    def get_client(self, instance_id: str) -> Optional[TelegramClient]:
        return self._clients.get(instance_id)

    async def stop_client(self, instance_id: str):
        async with self._lock:
            client = self._clients.pop(instance_id, None)
            if client:
                await client.disconnect()
                logger.info("Disconnected Telethon client for instance %s", instance_id)

    async def stop_all(self):
        async with self._lock:
            for instance_id, client in list(self._clients.items()):
                try:
                    await client.disconnect()
                except Exception as e:
                    logger.warning("Error disconnecting instance %s: %s", instance_id, e)
            self._clients.clear()
            logger.info("All Telethon clients disconnected")

    def get_connected_ids(self) -> list:
        return [iid for iid, c in self._clients.items() if c.is_connected()]


client_manager = TelegramClientManager()
