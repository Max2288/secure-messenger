from datetime import datetime

from pydantic import BaseModel


class MessageReadCreate(BaseModel):
    message_id: int
    user_id: int


class MessageReadResponse(BaseModel):
    id: int
    message_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MessageReadBulkCreate(BaseModel):
    message_ids: list[int]
    user_id: int
