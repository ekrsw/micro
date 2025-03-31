from datetime import datetime, timedelta
from typing import Any, Union, Tuple
import secrets
import string

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
        subject: Union[str, Any], expires_delta: timedelta = None
        ) -> str:
    """
    JWTアクセストークンを生成する
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    # UUIDをstr型に変換
    sub = str(subject) if hasattr(subject, 'hex') else subject
    to_encode = {"exp": expire, "sub": sub}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def generate_refresh_token(length: int = 64) -> str:
    """
    ランダムなリフレッシュトークンを生成する
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_refresh_token_expires() -> datetime:
    """
    リフレッシュトークンの有効期限を計算する
    """
    return datetime.utcnow() + timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証する
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化する
    """
    return pwd_context.hash(password)
