# tests/test_auth_register.py
"""Регистрация + OTP: подтверждение телефона, лимиты, A01 (роль не из запроса)."""
import pytest

from tests.conftest import register_user

PHONE = "+79995550101"


async def test_register_happy_path(client):
    data = await register_user(client, PHONE)
    assert data["user"]["phone"] == PHONE
    assert data["user"]["role"] == "client"
    assert data["access_token"]


async def test_register_role_is_never_taken_from_request(client):
    """A01: role в теле запроса игнорируется — всегда client."""
    r = await client.post("/api/v1/auth/register/send-code", json={"phone": PHONE})
    otp = r.json()
    r = await client.post(
        "/api/v1/auth/register",
        json={
            "phone": PHONE,
            "full_name": "Хочу Стать Админом",
            "password": "Testpass1",
            "request_id": otp["request_id"],
            "code": otp["dev_code"],
            "role": "admin",  # злонамеренное поле
        },
    )
    assert r.status_code == 200
    assert r.json()["user"]["role"] == "client"


async def test_register_rejects_wrong_code(client):
    r = await client.post("/api/v1/auth/register/send-code", json={"phone": PHONE})
    otp = r.json()
    wrong = "0000" if otp["dev_code"] != "0000" else "1111"
    r = await client.post(
        "/api/v1/auth/register",
        json={
            "phone": PHONE, "full_name": "Т", "password": "Testpass1",
            "request_id": otp["request_id"], "code": wrong,
        },
    )
    assert r.status_code == 400


async def test_otp_code_is_single_use(client):
    """Использованный код нельзя применить второй раз."""
    r = await client.post("/api/v1/auth/register/send-code", json={"phone": PHONE})
    otp = r.json()
    payload = {
        "phone": PHONE, "full_name": "Т", "password": "Testpass1",
        "request_id": otp["request_id"], "code": otp["dev_code"],
    }
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 200
    # повтор с тем же request_id/code — телефон другой, чтобы не упереться в 409
    payload["phone"] = "+79995550102"
    r = await client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 400


async def test_otp_verify_attempts_are_limited(client):
    """3 неверные попытки сжигают код — после них не проходит даже верный."""
    r = await client.post("/api/v1/auth/register/send-code", json={"phone": PHONE})
    otp = r.json()
    wrong = "0000" if otp["dev_code"] != "0000" else "1111"
    payload = {
        "phone": PHONE, "full_name": "Т", "password": "Testpass1",
        "request_id": otp["request_id"], "code": wrong,
    }
    for _ in range(3):
        assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 400
    payload["code"] = otp["dev_code"]
    r = await client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 400


async def test_duplicate_phone_rejected(client):
    await register_user(client, PHONE)
    r = await client.post("/api/v1/auth/register/send-code", json={"phone": PHONE})
    assert r.status_code == 409


async def test_weak_password_rejected(client):
    r = await client.post("/api/v1/auth/register/send-code", json={"phone": PHONE})
    otp = r.json()
    r = await client.post(
        "/api/v1/auth/register",
        json={
            "phone": PHONE, "full_name": "Т", "password": "password1",  # стоп-лист
            "request_id": otp["request_id"], "code": otp["dev_code"],
        },
    )
    assert r.status_code == 422


async def test_send_code_per_phone_limit(client):
    """Не более 5 кодов на номер (лимит по телефону, не по IP)."""
    import app.core.limiter as limiter_mod
    # IP-лимит slowapi (3/мин) обходим точечно: дёргаем внутренние функции
    allowed = [await limiter_mod.otp_send_allowed(PHONE) for _ in range(6)]
    assert allowed == [True] * 5 + [False]
