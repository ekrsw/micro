import logging
import asyncio
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from redis.exceptions import RedisError

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.db import AsyncSessionLocal
from app.db.redis import get_redis, close_redis_connection

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
    db_status = "not_checked"
    redis_status = "not_checked"
    
    # PostgreSQL接続チェック
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
    
    # Redis接続チェック
    retry_count = 0
    retry_delay = 1  # 秒
    while retry_count < max_retries:
        try:
            redis = await get_redis()
            await redis.ping()
            redis_status = "connected"
            break
        except RedisError as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"ヘルスチェック中のRedis接続エラー: {e}. リトライ中... ({retry_count}/{max_retries})")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # バックオフ
            else:
                logger.error(f"ヘルスチェック中のRedis接続に失敗しました: {e}")
                redis_status = f"error: {str(e)}"
        except Exception as e:
            logger.error(f"ヘルスチェック中に予期しないエラーが発生しました: {e}")
            redis_status = f"error: {str(e)}"
            break
    
    # 全体のステータスを判断
    is_healthy = "connected" in db_status and "connected" in redis_status
    
    response = {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": db_status,
        "redis": redis_status,
        "version": "0.1.0"
    }
    
    # いずれかの接続エラーの場合は503 Service Unavailableを返す
    if "error" in db_status or "error" in redis_status:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response
        )
    
    return response

@app.on_event("startup")
async def startup_event():
    max_retries = 5
    retry_count = 0
    retry_delay = 5  # 秒
    
    # PostgreSQLの初期化
    while retry_count < max_retries:
        try:
            await init_db()
            logger.info("データベースの初期化が完了しました")
            break
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"データベース初期化エラー: {e}. {retry_delay}秒後にリトライします ({retry_count}/{max_retries})...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # バックオフ
            else:
                logger.error(f"データベース初期化中にエラーが発生しました: {e}")
                # エラーをログに記録するだけで、アプリケーションは起動を続行
    
    # Redisの初期化
    retry_count = 0
    retry_delay = 5  # 秒
    while retry_count < max_retries:
        try:
            redis = await get_redis()
            await redis.ping()
            logger.info("Redisの接続が確立されました")
            return
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"Redis接続エラー: {e}. {retry_delay}秒後にリトライします ({retry_count}/{max_retries})...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # バックオフ
            else:
                logger.error(f"Redis接続中にエラーが発生しました: {e}")
                # エラーをログに記録するだけで、アプリケーションは起動を続行


@app.on_event("shutdown")
async def shutdown_event():
    # Redisの接続を閉じる
    try:
        await close_redis_connection()
        logger.info("Redisの接続を閉じました")
    except Exception as e:
        logger.error(f"Redis接続を閉じる際にエラーが発生しました: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
