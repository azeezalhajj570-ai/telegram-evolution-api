import logging

from telethon.errors import (
    AuthKeyUnregisteredError,
    ChatIdInvalidError,
    FloodWaitError,
    MessageIdInvalidError,
    PhoneCodeInvalidError,
    PhoneNumberBannedError,
    RpcCallFailError,
    RPCError,
    SessionPasswordNeededError,
)

logger = logging.getLogger(__name__)

ERROR_MAP: dict = {
    FloodWaitError: {"code": -32000, "message": "Rate limited by Telegram. Try again in {seconds} seconds."},
    RpcCallFailError: {"code": -32001, "message": "Telegram request failed. Please try again."},
    ChatIdInvalidError: {"code": -32002, "message": "Chat not found. Check the chat ID and try again."},
    MessageIdInvalidError: {"code": -32003, "message": "Message not found. It may have been deleted."},
    AuthKeyUnregisteredError: {"code": -32004, "message": "Instance is disconnected. Please re-authenticate."},
    PhoneCodeInvalidError: {"code": -32005, "message": "Invalid verification code. Please check and try again."},
    SessionPasswordNeededError: {"code": -32006, "message": "2FA is enabled. Please submit your 2FA password."},
    PhoneNumberBannedError: {"code": -32007, "message": "This phone number has been banned by Telegram."},
}


def mcp_error_from_telegram(exception: Exception) -> dict:
    for exc_type, mapping in ERROR_MAP.items():
        if isinstance(exception, exc_type):
            msg = mapping["message"]
            if isinstance(exception, FloodWaitError):
                msg = msg.format(seconds=exception.seconds)
            logger.warning("Mapped %s to error %s", type(exception).__name__, mapping["code"])
            return {"code": mapping["code"], "message": msg}
    if isinstance(exception, ValueError):
        if "not connected" in str(exception).lower() or "not connected" in str(exception):
            return {"code": -32008, "message": "Instance is not connected. Call connect_instance first."}
        return {"code": -32602, "message": str(exception)}
    if isinstance(exception, RPCError):
        logger.warning("Unmapped RPCError: %s", exception)
        return {"code": -32099, "message": f"Telegram API error: {exception}"}
    logger.exception("Unexpected error")
    return {"code": -32603, "message": "An unexpected internal error occurred"}
