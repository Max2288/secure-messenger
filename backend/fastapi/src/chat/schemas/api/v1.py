from enum import Enum

from pydantic import BaseModel, Field
from typing import Optional
from src.chat.models import ChatType


class ChatBase(BaseModel):
    name: str = Field(..., max_length=255)
    chat_type: ChatType


class ChatCreate(ChatBase):
    pass


class ChatUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    chat_type: Optional[ChatType] = None


class ChatResponse(ChatBase):
    id: int

    class Config:
        from_attributes = True
