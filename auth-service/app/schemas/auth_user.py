from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


# 共通のプロパティを持つUserBaseクラス
class UserBase(BaseModel):
    username: Optional[str] = None
    is_admin: Optional[bool] = False


# 新規ユーザー作成時に必要なプロパティ
class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=16)


# 新規監視やユーザー作成時に必要なプロパティ
class AdminUserCreate(UserBase):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=16)


# ユーザー更新時に使うプロパティ（パスワード更新は含まない）
class UserUpdate(UserBase):
    username: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


# パスワード更新時に使うプロパティ
class PasswordUpdate(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=16)
    new_password: str = Field(..., min_length=1, max_length=16)
    
    @field_validator('new_password')
    def passwords_must_not_match(cls, v, info):
        if 'current_password' in info.data and v == info.data['current_password']:
            raise ValueError('新しいパスワードは現在のパスワードと異なる必要があります')
        return v


# 管理者によるパスワード更新時に使うプロパティ
class AdminPasswordUpdate(BaseModel):
    user_id: UUID
    new_password: str = Field(..., min_length=1, max_length=16)


# ユーザー更新時に使うプロパティ（パスワード更新は含まない）
class UserUpdate(UserBase):
    username: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


# レスポンスとして返すユーザー情報
class UserInDBBase(UserBase):
    id: UUID
    username: str
    is_admin: bool
    is_active: bool
    user_id: Optional[UUID] = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


# APIレスポンスで使用するユーザースキーマ
class User(UserInDBBase):
    pass


# データベース内部で使用するスキーマ（パスワードハッシュを含む）
class UserInDB(UserInDBBase):
    hashed_password: str


# トークン関連のスキーマ
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None


# リフレッシュトークンリクエスト用のスキーマ（access_tokenを必須とする）
class RefreshTokenRequest(BaseModel):
    refresh_token: str
    access_token: str


# ログアウトリクエスト用のスキーマ（access_tokenを必須とする）
class LogoutRequest(BaseModel):
    refresh_token: str
    access_token: str


# 互換性のために残す（後で削除予定）
class RefreshToken(Token):
    pass


class TokenVerifyRequest(BaseModel):
    token: str


class TokenVerifyResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    roles: List[str] = []
    error: Optional[str] = None