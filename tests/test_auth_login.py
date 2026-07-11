# tests/test_auth_login.py
"""Вход: успех, неверный пароль, локаут по аккаунту, rate limit по IP."""
from app.core.limiter import (
    MAX_LOGIN_FAILS,
    is_account_locked,
    register_login_failure,
    reset_login_failures,
)
from tests.conftest import register_user

PHONE = "+79995550201"


async def test_login_success(client):
    await register_user(client, PHONE, password="Loginpass1")
    r = await client.post("/api/v1/auth/login", json={"phone": PHONE, "password": "Loginpass1"})
    assert r.status_code == 200
    body = r.json()
    assert body["access_token"] and body["user"]["phone"] == PHONE


async def test_login_wrong_password(client):
    await register_user(client, PHONE, password="Loginpass1")
    r = await client.post("/api/v1/auth/login", json={"phone": PHONE, "password": "WrongPass1"})
    assert r.status_code == 401


async def test_account_lockout_after_failures(client):
    """Уровень локаута по номеру (защита от распределённого брутфорса) —
    проверяем сам механизм, не завязываясь на IP-лимит slowapi."""
    assert not await is_account_locked(PHONE)
    for _ in range(MAX_LOGIN_FAILS):
        await register_login_failure(PHONE)
    assert await is_account_locked(PHONE)
    await reset_login_failures(PHONE)
    assert not await is_account_locked(PHONE)


async def test_login_rate_limited_or_locked_end_to_end(client):
    """6 подряд неудачных входов -> 429 (срабатывает slowapi по IP или локаут)."""
    await register_user(client, PHONE, password="Loginpass1")
    last = None
    for _ in range(6):
        last = await client.post(
            "/api/v1/auth/login", json={"phone": PHONE, "password": "WrongPass1"}
        )
    assert last.status_code == 429
