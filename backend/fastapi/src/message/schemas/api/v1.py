from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MessageBase(BaseModel):
    chat_id: int
    sender_id: int
    encrypted_payload: bytes


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    encrypted_payload: Optional[bytes] = None


class MessageResponse(MessageBase):
    id: int
    is_read: bool = False

    class Config:
        from_attributes = True
