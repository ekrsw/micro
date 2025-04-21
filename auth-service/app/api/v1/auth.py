import uuid
from typing import Any, List, Optional, Dict
from datetime import timedelta
from uuid import UUID
from jose import JWTError, jwt
from pydantic import ValidationError

from fastapi import APIRouter, Body, Depends, Header, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.crud.auth_user import crud_auth_user
from app.db.session import get_db
from app.messaging.rabbitmq import (
    publish_user_created,
    publish_user_updated,
    publish_user_deleted,
    publish_password_changed,
    publish_user_status_changed
)
from app.schemas.auth_user import (
    PasswordUpdate,
    AdminPasswordUpdate,
    AdminUserCreate,
    User as UserResponse,
    UserCreate,
    UserUpdate,
    Token,
    RefreshToken,
    RefreshTokenRequest,
    LogoutRequest, TokenVerifyRequest,
    TokenVerifyResponse
    )
from app.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    verify_refresh_token,
    revoke_refresh_token,
    verify_token,
    blacklist_token
)
from app.core.config import settings
from app.api.deps import validate_refresh_token, get_current_user, get_current_admin_user
from app.core.logging import get_request_logger, app_logger
from app.models.auth_user import AuthUser


router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
    ) -> Any:
    """
    一般ユーザーを登録するエンドポイント
    - 認証不要
    - 常にis_admin=Falseで登録される
    """
    logger = get_request_logger(request)
    logger.info(f"一般ユーザー登録リクエスト: {user_in.username}")
    
    # ユーザー名の重複チェック
    existing_user = await crud_auth_user.get_by_username(db, username=user_in.username)
    if existing_user:
        logger.warning(f"ユーザー登録失敗: ユーザー名 '{user_in.username}' は既に使用されています")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザー名は既に登録されています。"
        )
    
    # ユーザー作成
    new_user = await crud_auth_user.create(db, user_in)
    if not new_user:
        logger.error(f"ユーザー登録失敗: '{user_in.username}' の作成中にエラーが発生しました")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ユーザーの登録に失敗しました。"
        )
    
    # ユーザー作成イベントの発行
    '''
    try:
        user_data = {
            "id": new_user.id,
            "username": new_user.username,
            "is_admin": new_user.is_admin,
            "is_active": new_user.is_active
        }
        await publish_user_created(user_data)
        logger.info(f"ユーザー作成イベント発行: ID={new_user.id}")
    except Exception as e:
        # イベント発行の失敗はログに記録するだけで、APIレスポンスには影響させない
        logger.error(f"ユーザー作成イベント発行失敗: {str(e)}", exc_info=True)
    '''
    
    logger.info(f"ユーザー登録成功: ID={new_user.id}, ユーザー名={new_user.username}, 管理者={new_user.is_admin}")
    return new_user

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
    ) -> Any:
    """
    ユーザーログインとトークン発行のエンドポイント
    """
    logger = get_request_logger(request)
    logger.info(f"ログインリクエスト: ユーザー名={form_data.username}")
    
    # ユーザー認証
    db_user = await crud_auth_user.get_by_username(db, username=form_data.username)
    if not db_user:
        logger.warning(f"ログイン失敗: ユーザー名 '{form_data.username}' が存在しません")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # パスワード検証
    if not verify_password(form_data.password, db_user.hashed_password):
        logger.warning(f"ログイン失敗: ユーザー '{form_data.username}' のパスワードが不正です")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # アクセストークン生成
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": str(db_user.id),
              "user_id": str(db_user.user_id),
              "username": db_user.username},
        expires_delta=access_token_expires
    )
    
    # リフレッシュトークン生成
    refresh_token = await create_refresh_token(user_id=str(db_user.id))
    
    logger.info(f"ログイン成功: ユーザーID={db_user.id}, ユーザー名={db_user.username}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    request: Request,
    current_user: AuthUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
    ) -> Any:
    """
    全ユーザーを取得するエンドポイント（管理者のみ）
    """
    logger = get_request_logger(request)
    logger.info(f"全ユーザー取得リクエスト: 要求元={current_user.username}")
    
    users = await crud_auth_user.get_all_users(db)
    return users