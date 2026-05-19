import logging
import os
from typing import Optional

from app.security.api_keys import generate_api_key, hash_api_key, verify_api_key

logger = logging.getLogger(__name__)


def authenticate_stdio(api_key: Optional[str] = None) -> bool:
    from app.config import settings

    if not api_key:
        api_key = os.environ.get("MCP_API_KEY", "")
    if not api_key:
        logger.warning("MCP stdio auth failed: no API key provided")
        return False
    for configured_key in settings.api_keys_list:
        if configured_key == api_key:
            return True
        try:
            if verify_api_key(api_key, configured_key):
                return True
        except Exception:
            pass
    logger.warning("MCP stdio auth failed: invalid API key")
    return False


async def authenticate_sse(api_key: Optional[str]) -> bool:
    from app.config import settings

    if not api_key:
        return False
    if api_key in settings.api_keys_list:
        return True
    for configured_key in settings.api_keys_list:
        try:
            if verify_api_key(api_key, configured_key):
                return True
        except Exception:
            pass
    return False


async def resolve_instance_key(
    api_key: str,
) -> Optional[str]:
    from app.db.database import async_session
    from app.db.repositories import InstanceRepository

    async with async_session() as db:
        repo = InstanceRepository(db)
        all_instances = await repo.get_all()
        for inst in all_instances:
            if not inst.mcp_api_key_hash:
                continue
            try:
                if verify_api_key(api_key, inst.mcp_api_key_hash):
                    return str(inst.id)
            except Exception:
                pass
    return None


async def generate_instance_api_key(instance_id: str) -> str:
    from app.db.database import async_session
    from app.db.repositories import InstanceRepository

    raw_key = generate_api_key()
    key_hash = hash_api_key(raw_key)
    async with async_session() as db:
        repo = InstanceRepository(db)
        import uuid
        await repo.update(uuid.UUID(instance_id), mcp_api_key_hash=key_hash)
        await db.commit()
    return raw_key
