from datetime import datetime, timedelta
import time

import pytest
from jose import jwt

from app.core import security
from app.core.config import settings


def test_password_hash():
    """パスワードハッシュ化のテスト"""
    password = "testpassword"
    hashed_password = security.get_password_hash(password)
    
    # ハッシュ化されたパスワードが元のパスワードと異なることを確認
    assert hashed_password != password
    
    # 同じパスワードから異なるハッシュが生成されることを確認
    hashed_password2 = security.get_password_hash(password)
    assert hashed_password != hashed_password2


def test_password_verification():
    """パスワード検証のテスト"""
    password = "testpassword"
    hashed_password = security.get_password_hash(password)
    
    # 正しいパスワードで検証が成功することを確認
    assert security.verify_password(password, hashed_password) is True
    
    # 誤ったパスワードで検証が失敗することを確認
    assert security.verify_password("wrongpassword", hashed_password) is False


def test_access_token_creation():
    """アクセストークン生成のテスト"""
    user_id = "test-user-id"
    expires_delta = timedelta(minutes=15)
    
    # トークンの生成
    token = security.create_access_token(user_id, expires_delta)
    
    # トークンのデコード
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    # ペイロードの検証
    assert payload["sub"] == user_id
    
    # 有効期限の検証（誤差を許容）
    expected_exp = datetime.utcnow() + expires_delta
    token_exp = datetime.utcfromtimestamp(payload["exp"])
    assert abs((token_exp - expected_exp).total_seconds()) < 10


def test_access_token_default_expiry():
    """アクセストークンのデフォルト有効期限のテスト"""
    user_id = "test-user-id"
    
    # デフォルト有効期限でトークンを生成
    token = security.create_access_token(user_id)
    
    # トークンのデコード
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    # ペイロードの検証
    assert payload["sub"] == user_id
    
    # 有効期限の検証（誤差を許容）
    expected_exp = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_exp = datetime.utcfromtimestamp(payload["exp"])
    assert abs((token_exp - expected_exp).total_seconds()) < 10


def test_refresh_token_generation():
    """リフレッシュトークン生成のテスト"""
    # デフォルト長のトークン生成
    token = security.generate_refresh_token()
    assert len(token) == 64
    
    # カスタム長のトークン生成
    custom_length = 32
    token = security.generate_refresh_token(custom_length)
    assert len(token) == custom_length
    
    # 生成されたトークンが一意であることを確認
    token1 = security.generate_refresh_token()
    token2 = security.generate_refresh_token()
    assert token1 != token2


def test_refresh_token_expires():
    """リフレッシュトークンの有効期限計算のテスト"""
    # 有効期限の計算
    expires_at = security.create_refresh_token_expires()
    
    # 現在時刻からの差分を計算
    delta = expires_at - datetime.utcnow()
    
    # 設定された時間に近いことを確認（誤差を許容）
    expected_delta = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
    assert abs((delta - expected_delta).total_seconds()) < 10
