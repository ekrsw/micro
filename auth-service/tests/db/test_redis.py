import json
import time
import uuid
import asyncio

import pytest
import pytest_asyncio

from app.db.redis import (
    set_access_token,
    get_access_token,
    delete_access_token,
    add_to_blacklist,
    is_blacklisted,
)


@pytest.mark.asyncio
async def test_access_token_operations(redis_server, monkeypatch):
    """アクセストークンの操作テスト"""
    # get_redis()をモックして、テスト用Redisサーバーを返すようにする
    async def mock_get_redis():
        return redis_server
    monkeypatch.setattr("app.db.redis.get_redis", mock_get_redis)

    # テストデータ
    user_id = str(uuid.uuid4())
    token = "test_token"
    expires = 10  # 10秒
    
    # トークンの保存
    await set_access_token(user_id, token, expires)
    
    # トークンの取得と検証
    token_info = await get_access_token(token)
    assert token_info is not None
    assert token_info["user_id"] == user_id
    
    # Redisに直接アクセスして検証
    key = f"access_token:{token}"
    value = await redis_server.get(key)
    assert value is not None
    assert json.loads(value)["user_id"] == user_id
    
    # TTLの検証
    ttl = await redis_server.ttl(key)
    assert 0 < ttl <= expires
    
    # トークンの削除
    await delete_access_token(token)
    
    # 削除後の検証
    token_info = await get_access_token(token)
    assert token_info is None
    
    # Redisに直接アクセスして検証
    exists = await redis_server.exists(key)
    assert exists == 0


@pytest.mark.asyncio
async def test_token_expiry(redis_server, monkeypatch):
    """トークンの有効期限テスト"""
    # get_redis()をモックして、テスト用Redisサーバーを返すようにする
    async def mock_get_redis():
        return redis_server
    monkeypatch.setattr("app.db.redis.get_redis", mock_get_redis)

    # テストデータ
    user_id = str(uuid.uuid4())
    token = "expiry_test_token"
    expires = 2  # 2秒
    
    # トークンの保存
    await set_access_token(user_id, token, expires)
    
    # 保存直後の検証
    token_info = await get_access_token(token)
    assert token_info is not None
    
    # 有効期限が切れるまで待機
    await asyncio.sleep(2.5)
    
    # 有効期限後の検証
    token_info = await get_access_token(token)
    assert token_info is None


@pytest.mark.asyncio
async def test_blacklist_operations(redis_server, monkeypatch):
    """ブラックリスト操作のテスト"""
    # get_redis()をモックして、テスト用Redisサーバーを返すようにする
    async def mock_get_redis():
        return redis_server
    monkeypatch.setattr("app.db.redis.get_redis", mock_get_redis)

    # テストデータ
    token = "blacklist_test_token"
    expires = 10  # 10秒
    
    # 初期状態の検証
    is_in_blacklist = await is_blacklisted(token)
    assert is_in_blacklist is False
    
    # ブラックリストに追加
    await add_to_blacklist(token, expires)
    
    # 追加後の検証
    is_in_blacklist = await is_blacklisted(token)
    assert is_in_blacklist is True
    
    # Redisに直接アクセスして検証
    key = f"blacklist:{token}"
    value = await redis_server.get(key)
    assert value == "1"
    
    # TTLの検証
    ttl = await redis_server.ttl(key)
    assert 0 < ttl <= expires


@pytest.mark.asyncio
async def test_blacklist_expiry(redis_server, monkeypatch):
    """ブラックリストの有効期限テスト"""
    # get_redis()をモックして、テスト用Redisサーバーを返すようにする
    async def mock_get_redis():
        return redis_server
    monkeypatch.setattr("app.db.redis.get_redis", mock_get_redis)

    # テストデータ
    token = "blacklist_expiry_test_token"
    expires = 2  # 2秒
    
    # ブラックリストに追加
    await add_to_blacklist(token, expires)
    
    # 追加直後の検証
    is_in_blacklist = await is_blacklisted(token)
    assert is_in_blacklist is True
    
    # 有効期限が切れるまで待機
    await asyncio.sleep(2.5)
    
    # 有効期限後の検証
    is_in_blacklist = await is_blacklisted(token)
    assert is_in_blacklist is False
