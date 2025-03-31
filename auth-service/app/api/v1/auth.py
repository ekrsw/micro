import uuid
from datetime import timedelta, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_current_user
from app.core import security
from app.core.config import settings
from app.db.db import get_db
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
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
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
    
    # リフレッシュトークンの作成
    refresh_token = security.generate_refresh_token()
    refresh_token_expires = security.create_refresh_token_expires()
    
    # ユーザーにリフレッシュトークンを保存
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
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    リフレッシュトークンを使用して新しいアクセストークンを取得
    """
    # リフレッシュトークンでユーザーを検索
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
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": user.refresh_token,
    }


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    現在のユーザー情報を取得
    """
    return current_user
