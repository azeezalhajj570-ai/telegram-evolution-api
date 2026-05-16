from typing import Optional

from pydantic import BaseModel, Field


class MediaMessageResponse(BaseModel):
    message_id: int
    chat_id: int
    type: str
    status: str = "delivered"


class ReplyRequest(BaseModel):
    chat_id: int
    text: str = Field(..., min_length=1, max_length=4096)
    reply_to: int


class ForwardRequest(BaseModel):
    from_chat_id: int
    message_id: int
    to_chat_id: int


class EditMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)


class MessageActionResponse(BaseModel):
    message_id: int
    status: str


class ReactionRequest(BaseModel):
    emoji: str


class ReactionResponse(BaseModel):
    message_id: int
    reaction: str
    status: str = "applied"
