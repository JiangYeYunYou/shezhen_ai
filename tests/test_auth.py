import pytest
from httpx import AsyncClient

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post("/api/auth/register", json={
        "username": "测试用户",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["username"] == "测试用户"


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "username": "重复用户",
        "password": "password123"
    })
    
    response = await client.post("/api/auth/register", json={
        "username": "重复用户",
        "password": "password456"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "username": "登录用户",
        "password": "password123"
    })
    
    response = await client.post("/api/auth/login", json={
        "username": "登录用户",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "username": "密码测试",
        "password": "password123"
    })
    
    response = await client.post("/api/auth/login", json={
        "username": "密码测试",
        "password": "wrongpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 401
