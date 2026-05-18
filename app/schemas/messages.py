from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class SendMessageRequest(BaseModel):
    chat_id: Optional[int] = None
    username: Optional[str] = None
    phone_number: Optional[str] = None
    text: str = Field(..., min_length=1, max_length=4096)

    @model_validator(mode="after")
    def check_recipient(self):
        fields = [self.chat_id, self.username, self.phone_number]
        provided = [f for f in fields if f is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of chat_id, username, or phone_number must be provided")
        return self


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
