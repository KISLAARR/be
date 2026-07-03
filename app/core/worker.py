# app/core/worker.py
"""ARQ: настройки воркера и пул для постановки задач (блок 06).

Очередь живёт в том же Redis, что и rate limiting (settings.REDIS_URL).
Воркер — отдельный процесс:
    arq app.core.worker.WorkerSettings          # запуск
    arq --check app.core.worker.WorkerSettings  # health check (compose)
В проде — сервис arq-worker в docker-compose.prod.yml.

Постановка задачи из веб-процесса:
    pool = await get_arq_pool()
    await pool.enqueue_job("send_sms", phone, message)
"""
from __future__ import annotations

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import settings
from app.tasks import process_payment_webhook, send_sms

REDIS_SETTINGS = RedisSettings.from_dsn(settings.REDIS_URL)

# ── Пул для enqueue из веб-процесса (лениво, один на процесс) ────

_pool: ArqRedis | None = None


async def get_arq_pool() -> ArqRedis:
    global _pool
    if _pool is None:
        _pool = await create_pool(REDIS_SETTINGS)
    return _pool


async def close_arq_pool() -> None:
    """Закрытие пула на shutdown приложения (см. app/main.py)."""
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None


# ── Настройки воркера ────────────────────────────────────────────


class WorkerSettings:
    functions = [send_sms, process_payment_webhook]
    redis_settings = REDIS_SETTINGS
    max_tries = 5            # потолок для Retry из задач (см. app/tasks.py)
    job_timeout = 60         # сек на одну задачу
    keep_result = 3600       # результат храним час (отладка/идемпотентность)
    health_check_interval = 30  # воркер пишет health-ключ в Redis для --check
