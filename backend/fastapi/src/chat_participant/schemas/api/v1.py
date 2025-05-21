from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatParticipantBase(BaseModel):
    chat_id: int
    user_id: int
    left_at: Optional[datetime] = None


class ChatParticipantCreate(ChatParticipantBase):
    pass


class ChatParticipantUpdate(BaseModel):
    left_at: Optional[datetime] = None


class ChatParticipantResponse(ChatParticipantBase):
    id: int

    class Config:
        from_attributes = True