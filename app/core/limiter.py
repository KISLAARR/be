# app/core/limiter.py
"""Rate limiting (бриф 3.6).

Два уровня в приложении:
  - slowapi: лимит запросов на login-эндпоинты по IP (storage в Redis,
    чтобы счётчик был общим между воркерами uvicorn);
  - блокировка по аккаунту (телефону) против распределённого брутфорса.

Третий уровень — грубый флуд по IP на Nginx (см. README).
"""
from __future__ import annotations

import redis.asyncio as aioredis
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# slowapi хранит счётчики в Redis (sync-клиент создаёт сам по storage_uri)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=["200/day"],
)

# Отдельный async-клиент Redis для блокировки по аккаунту
_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


# --- Блокировка по аккаунту (телефону) ---
MAX_LOGIN_FAILS = 5
LOCKOUT_WINDOW_SECONDS = 15 * 60  # 15 минут


def _fail_key(phone: str) -> str:
    return f"login_fail:{phone}"


async def is_account_locked(phone: str) -> bool:
    """True, если по телефону превышен лимит неудачных попыток."""
    try:
        fails = await get_redis().get(_fail_key(phone))
    except Exception:
        # Redis недоступен — не блокируем легитимный вход (fail-open по локауту;
        # грубый перебор всё равно ловится slowapi/Nginx)
        return False
    return fails is not None and int(fails) >= MAX_LOGIN_FAILS


async def register_login_failure(phone: str) -> None:
    """Инкремент счётчика неудач с окном экспирации."""
    try:
        r = get_redis()
        key = _fail_key(phone)
        fails = await r.incr(key)
        if fails == 1:
            await r.expire(key, LOCKOUT_WINDOW_SECONDS)
    except Exception:
        pass


async def reset_login_failures(phone: str) -> None:
    """Успешный вход — сбрасываем счётчик."""
    try:
        await get_redis().delete(_fail_key(phone))
    except Exception:
        pass
