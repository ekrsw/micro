import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import status
from jose import jwt

from app.core.config import settings
from app.core import security


@pytest.mark.asyncio
async def test_register_user(client):
    """ユーザー登録のテスト"""
    # 正常系: 有効なデータでユーザーを登録
    user_data = {
        "username": "newuser",
        "password": "password123",
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "is_active" in data
    assert data["is_active"] is True
    
    # 異常系: 重複ユーザー名
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "このユーザー名は既に登録されています" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login(client, test_user):
    """ログインのテスト"""
    # 正常系: 有効な認証情報
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"
    
    # トークンの検証
    payload = jwt.decode(
        tokens["access_token"], settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert str(test_user["id"]) == payload["sub"]
    
    # 異常系: 無効なユーザー名
    login_data = {
        "username": "wronguser",
        "password": test_user["password"],
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # 異常系: 無効なパスワード
    login_data = {
        "username": test_user["username"],
        "password": "wrongpassword",
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_token(client, test_user, db):
    """リフレッシュトークンのテスト"""
    # ログインしてリフレッシュトークンを取得
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    tokens = response.json()
    refresh_token = tokens["refresh_token"]
    
    # 正常系: 有効なリフレッシュトークン
    refresh_data = {
        "refresh_token": refresh_token,
    }
    response = await client.post("/api/v1/auth/refresh", json=refresh_data)
    assert response.status_code == status.HTTP_200_OK
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] == refresh_token
    
    # 異常系: 無効なリフレッシュトークン
    refresh_data = {
        "refresh_token": "invalid_token",
    }
    response = await client.post("/api/v1/auth/refresh", json=refresh_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_logout(client, token_headers, test_user):
    """ログアウトのテスト"""
    # 正常系: 有効なトークンでログアウト
    response = await client.post("/api/v1/auth/logout", headers=token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "ログアウトしました"
    
    # ログアウト後のトークンでアクセスできないことを確認
    response = await client.get("/api/v1/auth/me", headers=token_headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_me_endpoint(client, token_headers, test_user):
    """ユーザー情報取得のテスト"""
    # 正常系: 認証済みユーザー
    response = await client.get("/api/v1/auth/me", headers=token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user["username"]
    assert str(data["id"]) == str(test_user["id"])
    
    # 異常系: 認証なし
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # 異常系: 無効なトークン
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get("/api/v1/auth/me", headers=invalid_headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
