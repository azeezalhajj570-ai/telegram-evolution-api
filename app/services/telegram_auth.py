import logging
import uuid

from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError, SessionPasswordNeededError
from telethon.sessions import StringSession
from telethon.tl.functions.auth import CheckPasswordRequest, SendCodeRequest
from telethon.tl.types.auth import SentCode

from app.config import settings
from app.db.repositories import InstanceRepository
from app.security.encryption import encrypt
from app.services.telegram_manager import client_manager

logger = logging.getLogger(__name__)


async def send_code(instance_id: uuid.UUID, phone_number: str, repo: InstanceRepository) -> str:
    client = TelegramClient(StringSession(), settings.telegram_api_id, settings.telegram_api_hash)
    await client.connect()
    result: SentCode = await client(SendCodeRequest(phone_number, settings.telegram_api_id, settings.telegram_api_hash))
    await client.disconnect()

    await repo.update(instance_id, phone_number=phone_number, phone_code_hash=result.phone_code_hash, status="code_sent")
    logger.info("Login code sent for instance %s", instance_id)
    return result.phone_code_hash


async def verify_code(instance_id: uuid.UUID, code: str, repo: InstanceRepository) -> dict:
    instance = await repo.get(instance_id)
    if not instance or not instance.phone_code_hash:
        raise ValueError("No active login flow")

    client = TelegramClient(StringSession(), settings.telegram_api_id, settings.telegram_api_hash)
    await client.connect()

    try:
        await client.sign_in(phone=instance.phone_number, code=code, phone_code_hash=instance.phone_code_hash)
    except SessionPasswordNeededError:
        await repo.update(instance_id, status="awaiting_2fa")
        await client.disconnect()
        return {"status": "awaiting_2fa", "twofa_required": True}
    except PhoneCodeInvalidError:
        await client.disconnect()
        raise ValueError("Invalid code")

    session_str = client.session.save()
    encrypted = encrypt(session_str, settings.encryption_key.encode())
    await repo.update(instance_id, session_encrypted=encrypted, phone_code_hash=None, status="authenticated")
    await client.disconnect()
    logger.info("Instance %s authenticated successfully", instance_id)
    return {"status": "authenticated", "twofa_required": False}


async def submit_2fa(instance_id: uuid.UUID, password: str, repo: InstanceRepository) -> dict:
    instance = await repo.get(instance_id)
    if not instance or instance.status != "awaiting_2fa":
        raise ValueError("2FA not required or invalid state")

    client = TelegramClient(StringSession(), settings.telegram_api_id, settings.telegram_api_hash)
    await client.connect()
    await client.sign_in(phone=instance.phone_number)

    try:
        await client(CheckPasswordRequest(password))
    except Exception as e:
        await client.disconnect()
        logger.warning("2FA failed for instance %s: %s", instance_id, e)
        raise ValueError("Invalid 2FA password")

    session_str = client.session.save()
    encrypted = encrypt(session_str, settings.encryption_key.encode())
    await repo.update(instance_id, session_encrypted=encrypted, status="authenticated")
    await client.disconnect()
    logger.info("Instance %s 2FA completed", instance_id)
    return {"status": "authenticated", "twofa_required": False}
