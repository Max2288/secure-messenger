from typing import Optional

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    username: str = Field(..., max_length=150)
    password_hash: str
    public_key: str


class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, max_length=150)
    password_hash: Optional[str] = None
    public_key: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    public_key: str

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    username: str
    password_hash: str