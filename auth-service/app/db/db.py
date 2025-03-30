from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 非同期データベース接続URLの取得
ASYNC_DATABASE_URL = settings.ASYNC_DATABASE_URL

# 非同期エンジンの作成（接続エラー時のリトライを設定）
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # 接続前にpingを実行して接続状態を確認
    pool_recycle=3600,   # 接続を1時間ごとにリサイクル
    connect_args={
        "command_timeout": 10  # 接続コマンドのタイムアウトを10秒に設定
    }
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)

Base = declarative_base()


async def get_db():
    """
    非同期データベースセッションの依存関係
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
