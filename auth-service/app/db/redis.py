from typing import Optional, Any, Dict
import json
from redis import asyncio as aioredis
from redis.asyncio.client import Redis

from app.core.config import settings

# Redisクライアントのインスタンス
redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """
    Redisクライアントの依存関係
    """
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def close_redis_connection():
    """
    Redisクライアントの接続を閉じる
    """
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def set_access_token(user_id: str, token: str, expires: int) -> None:
    """
    アクセストークンをRedisに保存する
    
    Args:
        user_id: ユーザーID
        token: アクセストークン
        expires: 有効期限（秒）
    """
    redis = await get_redis()
    key = f"access_token:{token}"
    value = json.dumps({"user_id": user_id})
    await redis.set(key, value, ex=expires)


async def get_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    アクセストークンをRedisから取得する
    
    Args:
        token: アクセストークン
        
    Returns:
        トークン情報（ユーザーIDなど）
    """
    redis = await get_redis()
    key = f"access_token:{token}"
    value = await redis.get(key)
    if value:
        return json.loads(value)
    return None


async def delete_access_token(token: str) -> None:
    """
    アクセストークンをRedisから削除する
    
    Args:
        token: アクセストークン
    """
    redis = await get_redis()
    key = f"access_token:{token}"
    await redis.delete(key)


async def add_to_blacklist(token: str, expires: int) -> None:
    """
    トークンをブラックリストに追加する
    
    Args:
        token: ブラックリストに追加するトークン
        expires: 有効期限（秒）
    """
    redis = await get_redis()
    key = f"blacklist:{token}"
    await redis.set(key, "1", ex=expires)


async def is_blacklisted(token: str) -> bool:
    """
    トークンがブラックリストに含まれているかチェックする
    
    Args:
        token: チェックするトークン
        
    Returns:
        ブラックリストに含まれている場合はTrue
    """
    redis = await get_redis()
    key = f"blacklist:{token}"
    return await redis.exists(key) == 1
