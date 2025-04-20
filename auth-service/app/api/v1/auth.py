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
    existing_user = await user.get_by_username(db, username=user_in.username)
    if existing_user:
        logger.warning(f"ユーザー登録失敗: ユーザー名 '{user_in.username}' は既に使用されています")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このユーザー名は既に登録されています。"
        )
    
    # ユーザー作成
    new_user = await user.create(db, user_in)
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