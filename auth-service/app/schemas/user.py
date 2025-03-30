from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserInDBBase(UserBase):
    id: str
    email: EmailStr
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


class TokenPayload(BaseModel):
    sub: Optional[str] = None
