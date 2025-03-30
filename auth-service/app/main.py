import logging
import asyncio
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.db import AsyncSessionLocal

# ロガーの設定
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Auth Service API",
    description="認証サービスAPI",
    version="0.1.0",
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの登録
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Auth Service API"}

@app.get("/health")
async def health_check():
    # データベース接続の確認（リトライロジック付き）
    max_retries = 3
    retry_count = 0
    retry_delay = 1  # 秒
    
    while retry_count < max_retries:
        try:
            async with AsyncSessionLocal() as db:
                # 非同期でSQLを実行
                result = await db.execute(text("SELECT 1"))
                await result.fetchone()
                db_status = "connected"
                break
        except OperationalError as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"ヘルスチェック中のデータベース接続エラー: {e}. リトライ中... ({retry_count}/{max_retries})")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # バックオフ
            else:
                logger.error(f"ヘルスチェック中のデータベース接続に失敗しました: {e}")
                db_status = f"error: {str(e)}"
        except Exception as e:
            logger.error(f"ヘルスチェック中に予期しないエラーが発生しました: {e}")
            db_status = f"error: {str(e)}"
            break
    
    response = {
        "status": "healthy" if "connected" in db_status else "unhealthy",
        "database": db_status,
        "version": "0.1.0"
    }
    
    # データベース接続エラーの場合は503 Service Unavailableを返す
    if "error" in db_status:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response
        )
    
    return response

@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
    except Exception as e:
        logger.error(f"アプリケーション起動中にエラーが発生しました: {e}")
        # エラーをログに記録するだけで、アプリケーションは起動を続行
        # これにより、データベースが利用できない場合でもAPIの一部は機能する
