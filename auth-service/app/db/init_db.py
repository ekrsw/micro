import logging
import uuid
import asyncio
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import OperationalError

from app.db.db import Base, engine, AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import settings

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_initial_admin(db: AsyncSession) -> None:
    """
    初期管理者ユーザーの作成
    """
    try:
        # 管理者ユーザーが存在するか確認
        result = await db.execute(select(User).filter(User.username == "admin"))
        admin = result.scalars().first()
        if admin:
            logger.info("管理者ユーザーは既に存在します")
            return

        # 管理者ユーザーの作成
        admin_user = User(
            id=uuid.uuid4(),
            username=settings.ADMIN_USERNAME,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            is_active=True,
            is_admin=True,
        )
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        logger.info(f"管理者ユーザーを作成しました: {admin_user.username}")
    except Exception as e:
        await db.rollback()
        logger.error(f"管理者ユーザー作成中にエラーが発生しました: {e}")
        raise


async def init_db() -> None:
    """
    データベースの初期化（リトライロジック付き）
    """
    max_retries = 5
    retry_count = 0
    retry_delay = 5  # 秒

    while retry_count < max_retries:
        try:
            logger.info("データベースの初期化を開始します...")
            
            # テーブルの作成
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("テーブルの作成が完了しました")
            
            # 初期データの作成
            async with AsyncSessionLocal() as db:
                await create_initial_admin(db)
                logger.info("データベースの初期化が完了しました")
            
            # 成功したらループを抜ける
            return
        
        except OperationalError as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"データベース接続エラー: {e}. {retry_delay}秒後にリトライします ({retry_count}/{max_retries})...")
                await asyncio.sleep(retry_delay)
                # リトライ間隔を徐々に増やす（バックオフ）
                retry_delay *= 1.5
            else:
                logger.error(f"データベース初期化に失敗しました。最大リトライ回数に達しました: {e}")
                raise
        except Exception as e:
            logger.error(f"データベース初期化中にエラーが発生しました: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(init_db())
