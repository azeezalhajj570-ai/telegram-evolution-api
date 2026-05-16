from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    chat_id: int
    text: str = Field(..., min_length=1, max_length=4096)


class SendMessageResponse(BaseModel):
    message_id: int
    chat_id: int
    status: str


class ChatInfo(BaseModel):
    chat_id: int
    title: str
    type: str
    unread_count: int = 0
    last_message: Optional[dict] = None


class ChatListResponse(BaseModel):
    chats: List[ChatInfo]


class MessageInfo(BaseModel):
    message_id: int
    chat_id: int
    sender_id: int
    text: str
    date: datetime
    is_outgoing: bool = False


class MessagesResponse(BaseModel):
    messages: List[MessageInfo]
