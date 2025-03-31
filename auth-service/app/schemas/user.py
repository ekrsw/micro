from typing import Optional
import uuid

from pydantic import BaseModel


class UserBase(BaseModel):
    username: Optional[str] = None


class UserCreate(UserBase):
    username: str
    password: str


class UserInDBBase(UserBase):
    id: uuid.UUID
    username: str
    is_active: bool = True
    is_admin: bool = False

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class TokenPayload(BaseModel):
    sub: Optional[uuid.UUID] = None
    exp: Optional[int] = None


class RefreshToken(BaseModel):
    refresh_token: str
