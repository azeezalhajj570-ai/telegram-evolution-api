from typing import Any


def sanitize_message(msg: dict) -> dict:
    """Trim a Telegram message to essential fields for AI context."""
    text = msg.get("text", "")
    msg_type = msg.get("type", "")
    if not msg_type:
        if msg.get("is_outgoing"):
            msg_type = "outgoing"
        else:
            msg_type = "incoming"
    return {
        "id": str(msg.get("message_id", msg.get("id", ""))),
        "from": str(msg.get("sender_id", "")),
        "text": (text[:500] + "...") if len(text) > 500 else text,
        "type": msg_type,
        "timestamp": msg.get("date", ""),
    }


def sanitize_chat(chat: dict) -> dict:
    """Trim a Telegram chat/dialog to essential fields."""
    lm = chat.get("last_message")
    summary = None
    if lm:
        t = lm.get("text", "")
        summary = (t[:200] + "...") if len(t) > 200 else t
    return {
        "id": str(chat.get("chat_id", chat.get("id", ""))),
        "title": chat.get("title", "Unknown"),
        "type": chat.get("type", "chat"),
        "unread": chat.get("unread_count", 0),
        "last_message": summary or "",
    }


def sanitize_contact(contact: dict) -> dict:
    """Trim a Telegram contact to essential fields."""
    first = contact.get("first_name", "")
    last = contact.get("last_name", "")
    name = f"{first} {last}".strip() or contact.get("username", "") or "Unknown"
    return {
        "id": str(contact.get("user_id", contact.get("id", ""))),
        "name": name,
        "phone": contact.get("phone", ""),
        "username": contact.get("username", ""),
    }


def sanitize_group(group: dict) -> dict:
    """Trim a Telegram group/channel to essential fields."""
    return {
        "id": str(group.get("group_id", group.get("channel_id", group.get("id", "")))),
        "title": group.get("title", "Unknown"),
        "type": "group" if "group_id" in group else "channel",
        "members": group.get("participants_count", 0),
    }
