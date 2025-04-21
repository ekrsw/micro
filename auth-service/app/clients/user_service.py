import httpx
from fastapi import HTTPException, status
from uuid import UUID

from app.core.config import settings
from app.core.logging import app_logger

async def get_user_info_from_user_service(user_id: UUID) -> dict:
    """
    User Serviceからユーザー情報を取得する関数
    
    Args:
        user_id: ユーザーID
        
    Returns:
        dict: ユーザー情報を含む辞書（is_admin属性などを含む）
        
    Raises:
        HTTPException: リクエスト失敗時
    """
    # User ServiceのURLを設定
    user_service_url = settings.USER_SERVICE_URL  # 設定から取得
    endpoint = f"{user_service_url}/api/v1/profile/{user_id}"
    
    try:
        async with httpx.AsyncClient() as client:
            # User Serviceにリクエスト送信
            response = await client.get(endpoint, timeout=10.0)
            
            # エラーチェック
            if response.status_code == status.HTTP_404_NOT_FOUND:
                app_logger.warning(f"ユーザーID '{user_id}' がUser Serviceに存在しません")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="指定されたユーザーが見つかりません"
                )
            
            # その他のHTTPエラー
            response.raise_for_status()
            
            # JSONレスポンスを取得
            user_info = response.json()
            
            # 必要な情報を抽出して返却
            return {
                "id": user_info.get("id"),
                "username": user_info.get("username"),
                "fullname": user_info.get("fullname"),
                "is_admin": user_info.get("is_admin", False),
                "is_active": user_info.get("is_active", True)
            }
            
    except httpx.RequestError as e:
        # 接続エラー
        app_logger.error(f"User Serviceへの接続エラー: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ユーザー情報サービスに接続できません。しばらく経ってからお試しください。"
        )
    
    except httpx.HTTPStatusError as e:
        # HTTPエラー（404以外）
        app_logger.error(f"User Serviceからのレスポンスエラー: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ユーザー情報の取得中にエラーが発生しました"
        )