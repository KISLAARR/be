# app/tasks.py
"""Фоновые задачи (ARQ) — блок 06 роадмапа.

Выполняются arq-воркером вне HTTP-запроса:
    arq app.core.worker.WorkerSettings

Ретраи: на временных сбоях (сеть, 5xx провайдера, недоступность БД) задача
поднимает arq.worker.Retry с растущей задержкой; после WorkerSettings.max_tries
попыток job уходит в failed. Постоянные ошибки (кривой payload) не ретраим.
"""
from __future__ import annotations

import logging
from typing import Any

from arq.worker import Retry

logger = logging.getLogger(__name__)

# Задержка перед повтором = RETRY_BASE_DELAY * номер попытки (5с, 10с, 15с…)
RETRY_BASE_DELAY = 5


class TransientTaskError(Exception):
    """Временный сбой (сеть/провайдер/БД) — задачу нужно повторить."""


def _retry(ctx: dict[str, Any], exc: Exception) -> Retry:
    """Retry с линейным backoff по номеру текущей попытки."""
    return Retry(defer=RETRY_BASE_DELAY * ctx["job_try"])


def _mask_phone(phone: str) -> str:
    """Телефон в логах не светим целиком: +7999***99."""
    return f"{phone[:5]}***{phone[-2:]}" if len(phone) > 7 else "***"


# ── SMS / flash-call ─────────────────────────────────────────────


async def _send_via_provider(phone: str, message: str) -> None:
    """Единственная точка вызова SMS/flash-call-провайдера.

    Провайдер подключается в блоке 07 (OTP): здесь появится HTTP-вызов его
    API; сетевые ошибки и 5xx оборачивать в TransientTaskError, ошибки
    вида «невалидный номер» — пробрасывать как есть (ретрай не поможет).
    Пока провайдера нет — dev-заглушка, пишет сообщение в лог.
    """
    logger.info("[dev-заглушка SMS] %s: %s", _mask_phone(phone), message)


async def send_sms(ctx: dict[str, Any], phone: str, message: str) -> str:
    """Отправка SMS вне запроса (OTP-коды, уведомления о записи)."""
    try:
        await _send_via_provider(phone, message)
    except TransientTaskError as exc:
        logger.warning(
            "send_sms %s: временный сбой (попытка %d): %s",
            _mask_phone(phone), ctx["job_try"], exc,
        )
        raise _retry(ctx, exc) from exc
    logger.info("send_sms %s: отправлено (попытка %d)", _mask_phone(phone), ctx["job_try"])
    return "sent"


# ── Вебхуки оплаты (Т-Касса) ─────────────────────────────────────


async def _apply_payment_update(payload: dict[str, Any]) -> None:
    """Применение статуса платежа к БД (подписки, блок 09).

    Здесь появится: проверка Token (подпись Т-Кассы), поиск платежа по
    OrderId, идемпотентное обновление статуса подписки. Ошибки подключения
    к БД оборачивать в TransientTaskError. Пока блока 09 нет — заглушка.
    """
    logger.info(
        "[dev-заглушка payment] OrderId=%s Status=%s",
        payload.get("OrderId"), payload.get("Status"),
    )


async def process_payment_webhook(ctx: dict[str, Any], payload: dict[str, Any]) -> str:
    """Обработка вебхука оплаты вне запроса.

    Эндпоинт вебхука (блок 09) сразу отвечает Т-Кассе "OK" и кладёт payload
    в очередь. Дедупликация повторных доставок — на стороне enqueue через
    _job_id=f"tkassa:{OrderId}:{Status}" (arq не ставит дубль job_id).
    """
    if not payload.get("OrderId"):
        # Постоянная ошибка: без OrderId платёж не идентифицировать, ретрай бессмыслен
        logger.error("process_payment_webhook: payload без OrderId, отбрасываем: %r", payload)
        return "rejected"
    try:
        await _apply_payment_update(payload)
    except TransientTaskError as exc:
        logger.warning(
            "process_payment_webhook OrderId=%s: временный сбой (попытка %d): %s",
            payload["OrderId"], ctx["job_try"], exc,
        )
        raise _retry(ctx, exc) from exc
    logger.info("process_payment_webhook OrderId=%s: обработан", payload["OrderId"])
    return "processed"
