import logging
import uuid
from sqlalchemy.orm import Session

from app.db.db import Base, engine, SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

# ロガーの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_initial_admin(db: Session) -> None:
    """
    初期管理者ユーザーの作成
    """
    try:
        # 管理者ユーザーが存在するか確認
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if admin:
            logger.info("管理者ユーザーは既に存在します")
            return

        # 管理者ユーザーの作成
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@example.com",
            hashed_password=get_password_hash("adminpassword"),
            is_active=True,
            is_admin=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info(f"管理者ユーザーを作成しました: {admin_user.email}")
    except Exception as e:
        db.rollback()
        logger.error(f"管理者ユーザー作成中にエラーが発生しました: {e}")
        raise


def init_db() -> None:
    """
    データベースの初期化
    """
    try:
        logger.info("データベースの初期化を開始します...")
        
        # テーブルの作成
        Base.metadata.create_all(bind=engine)
        logger.info("テーブルの作成が完了しました")
        
        # 初期データの作成
        db = SessionLocal()
        try:
            create_initial_admin(db)
            logger.info("データベースの初期化が完了しました")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"データベース初期化中にエラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    init_db()
