from typing import AsyncGenerator, Optional
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from redis.asyncio.client import Redis

from app.core import security
from app.core.config import settings
from app.db.db import get_db
from app.db.redis import get_redis, is_blacklisted, get_access_token
from app.models.user import User
from app.schemas.user import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_current_user(
        db: AsyncSession = Depends(get_db), 
        redis: Redis = Depends(get_redis),
        token: str = Depends(reusable_oauth2)
        ) -> User:
    try:
        # トークンがブラックリストに含まれているかチェック
        if await is_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="トークンが無効化されています",
                )
        
        # Redisからトークン情報を取得
        token_info = await get_access_token(token)
        
        if token_info:
            # Redisにトークンが存在する場合、ユーザーIDを取得
            user_id = token_info.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="トークン情報が不正です",
                    )
        else:
            # Redisにトークンが存在しない場合、JWTをデコード
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                    )
                token_data = TokenPayload(**payload)
                user_id = str(token_data.sub)
            except (jwt.JWTError, ValidationError):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="認証情報が無効です",
                    )
        
        # ユーザー情報を取得
        result = await db.execute(select(User).filter(User.id == uuid.UUID(user_id)))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="ユーザーが無効です")
        return user
    except ValueError:
        # UUIDの変換エラー
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="認証情報が無効です",
            )
