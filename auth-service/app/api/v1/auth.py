import uuid
from datetime import timedelta, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from redis.asyncio.client import Redis
from jose import jwt
from pydantic import ValidationError

from app.api.deps import get_current_user, reusable_oauth2
from app.core import security
from app.core.config import settings
from app.db.db import get_db
from app.db.redis import get_redis, set_access_token, delete_access_token, add_to_blacklist
from app.models.user import User
from app.schemas.user import Token, User as UserSchema, UserCreate, RefreshToken

router = APIRouter()


@router.post("/register", response_model=UserSchema)
async def register_user(
    user_in: UserCreate, db: AsyncSession = Depends(get_db)
    ) -> Any:
    """
    ユーザー登録
    """
    # ユーザー名の重複チェック
    result = await db.execute(select(User).filter(User.username == user_in.username))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザー名は既に登録されています",
            )
    
    # ユーザー作成
    user = User(
        id=uuid.uuid4(),
        username=user_in.username,
        hashed_password=security.get_password_hash(user_in.password),
        is_active=True,
        )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), 
    redis: Redis = Depends(get_redis),
    form_data: OAuth2PasswordRequestForm = Depends()
    ) -> Any:
    """
    OAuth2互換のトークンログインを取得
    """
    result = await db.execute(select(User).filter(User.username == form_data.username))
    user = result.scalars().first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ユーザーが無効です",
        )
    
    # アクセストークンの作成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id,
        expires_delta=access_token_expires
    )
    
    # アクセストークンをRedisに保存
    await set_access_token(
        str(user.id), 
        access_token, 
        settings.ACCESS_TOKEN_REDIS_EXPIRE_SECONDS
    )
    
    # リフレッシュトークンの作成
    refresh_token = security.generate_refresh_token()
    refresh_token_expires = security.create_refresh_token_expires()
    
    # リフレッシュトークンをPostgreSQLに保存
    user.refresh_token = refresh_token
    user.refresh_token_expires_at = refresh_token_expires
    await db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token_in: RefreshToken = Body(...),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """
    リフレッシュトークンを使用して新しいアクセストークンを取得
    """
    # リフレッシュトークンでユーザーを検索（PostgreSQLから）
    result = await db.execute(select(User).filter(User.refresh_token == refresh_token_in.refresh_token))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なリフレッシュトークンです",
        )
    
    # リフレッシュトークンの有効期限をチェック
    if not user.refresh_token_expires_at or user.refresh_token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="リフレッシュトークンの有効期限が切れています",
        )
    
    # 新しいアクセストークンを生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id,
        expires_delta=access_token_expires
    )
    
    # 新しいアクセストークンをRedisに保存
    await set_access_token(
        str(user.id), 
        access_token, 
        settings.ACCESS_TOKEN_REDIS_EXPIRE_SECONDS
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": user.refresh_token,
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(reusable_oauth2),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
) -> Any:
    """
    ユーザーをログアウトし、トークンを無効化する
    """
    # アクセストークンをRedisから削除
    await delete_access_token(token)
    
    # トークンをブラックリストに追加
    # JWTの有効期限まで保持する
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        exp = payload.get("exp")
        if exp:
            # 現在時刻からの残り秒数を計算
            current_timestamp = datetime.utcnow().timestamp()
            remaining_seconds = max(1, int(exp - current_timestamp))
            await add_to_blacklist(token, remaining_seconds)
    except (jwt.JWTError, ValidationError):
        # トークンが無効な場合でも、念のためブラックリストに追加（1時間）
        await add_to_blacklist(token, 3600)
    
    # リフレッシュトークンを無効化
    current_user.refresh_token = None
    current_user.refresh_token_expires_at = None
    await db.commit()
    
    return {"message": "ログアウトしました"}


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    現在のユーザー情報を取得
    """
    return current_user
