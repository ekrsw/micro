import asyncio
import os
import uuid
from typing import AsyncGenerator, Dict, Generator

import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import fakeredis.aioredis

from app.core.config import settings
from app.core import security
from app.db.db import Base, get_db
from app.db.redis import get_redis
from app.main import app as main_app
from app.models.user import User


# テスト環境変数の設定
os.environ["TESTING"] = "True"


# テスト用データベースエンジンの設定
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://test:test@postgres-test:5432/test_auth_db")
engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# テスト用Redisインスタンスの設定
@pytest.fixture
def redis_server():
    server = fakeredis.aioredis.FakeRedis()
    yield server
    asyncio.run(server.close())


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    # テスト用データベースの作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # テストセッションの作成
    async with TestingSessionLocal() as session:
        yield session
    
    # テスト後のクリーンアップ
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# テスト用アプリケーションの設定
@pytest.fixture
def app() -> FastAPI:
    return main_app


# テスト用クライアントの設定
@pytest_asyncio.fixture
async def client(app: FastAPI, db: AsyncSession, redis_server) -> AsyncGenerator[TestClient, None]:
    # 依存関係のオーバーライド
    async def override_get_db():
        yield db
    
    async def override_get_redis():
        yield redis_server
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    
    async with TestClient(app) as client:
        yield client
    
    # 依存関係のリセット
    app.dependency_overrides = {}


# テスト用ユーザーの作成
@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> Dict:
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        username="testuser",
        hashed_password=security.get_password_hash("password"),
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return {
        "id": user_id,
        "username": "testuser",
        "password": "password",
    }


# テスト用管理者ユーザーの作成
@pytest_asyncio.fixture
async def test_admin(db: AsyncSession) -> Dict:
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        username="testadmin",
        hashed_password=security.get_password_hash("adminpassword"),
        is_active=True,
        is_admin=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return {
        "id": user_id,
        "username": "testadmin",
        "password": "adminpassword",
    }


# テスト用トークンの生成
@pytest_asyncio.fixture
async def token_headers(client: TestClient, test_user: Dict) -> Dict:
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    tokens = response.json()
    
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# テスト用管理者トークンの生成
@pytest_asyncio.fixture
async def admin_token_headers(client: TestClient, test_admin: Dict) -> Dict:
    login_data = {
        "username": test_admin["username"],
        "password": test_admin["password"],
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    tokens = response.json()
    
    return {"Authorization": f"Bearer {tokens['access_token']}"}
