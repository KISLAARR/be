# app/tg_bot.py
"""Telegram-бот подтверждения номера телефона (блок 18).

Запуск: python -m app.tg_bot — отдельный контейнер рядом с приложением.
Long polling, не webhook: боту не нужны ни порт, ни маршрут в Caddy,
только исходящие соединения к api.telegram.org и Redis.

Контракт с приложением — исключительно Redis-запись otp:{request_id}
(создаёт app/services/otp.py со status=pending): бот после проверки
контакта переводит её в confirmed, дальше работает обычный verify_code.

Ключевая проверка безопасности: принимается ТОЛЬКО собственный контакт
отправителя (contact.user_id == from_user.id) — пересланный чужой контакт
не подтверждает ничего.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from app.core.config import settings
from app.core.limiter import get_redis
from app.schemas.user import try_normalize_phone
from app.services.otp import (
    TG_STATUS_CONFIRMED,
    TG_STATUS_PENDING,
    _hash,
    _key,
    _mask_phone,
)

logger = logging.getLogger("tg_bot")

VERDICT_OK = "ok"
VERDICT_NOT_FOUND = "not_found"
VERDICT_FOREIGN_CONTACT = "foreign_contact"
VERDICT_PHONE_MISMATCH = "phone_mismatch"


def _pending_key(user_id: int) -> str:
    """Какой request_id сейчас подтверждает этот Telegram-пользователь.

    Храним в Redis, а не в памяти бота: состояние переживает рестарт
    контейнера и деплой. TTL тот же, что у самой верификации.
    """
    return f"otp:tg-pending:{user_id}"


def check_contact(
    record: dict,
    contact_user_id,
    sender_id: int,
    contact_phone: str,
) -> str:
    """Чистая проверка контакта против записи верификации (без aiogram — тестируемо).

    Порядок важен: сначала валидность записи, затем принадлежность контакта
    отправителю, затем совпадение номера.
    """
    if (
        not record
        or record.get("channel") != "telegram"
        or record.get("status") != TG_STATUS_PENDING
    ):
        return VERDICT_NOT_FOUND
    if contact_user_id is None or contact_user_id != sender_id:
        return VERDICT_FOREIGN_CONTACT
    phone = try_normalize_phone(contact_phone or "")
    if not phone or _hash(phone) != record.get("phone_hash"):
        return VERDICT_PHONE_MISMATCH
    return VERDICT_OK


_CONTACT_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


async def on_start(message: Message, command: CommandObject) -> None:
    """/start <request_id> из deep link'а на странице регистрации."""
    token = (command.args or "").strip()
    r = get_redis()
    record = await r.hgetall(_key(token)) if token else {}

    if not record or record.get("channel") != "telegram":
        await message.answer(
            "Ссылка устарела или открыта без сайта. Вернитесь на страницу "
            "регистрации Руми и нажмите «Подтвердить в Telegram» ещё раз."
        )
        return

    await r.set(
        _pending_key(message.from_user.id),
        token,
        ex=settings.OTP_TTL_MINUTES * 60,
    )
    await message.answer(
        "Здравствуйте! Это подтверждение номера для Руми.\n\n"
        "Нажмите кнопку ниже — Telegram передаст нам ваш номер, и мы сверим "
        "его с указанным при регистрации. Ничего вводить не нужно.",
        reply_markup=_CONTACT_KB,
    )


async def on_contact(message: Message) -> None:
    r = get_redis()
    token = await r.get(_pending_key(message.from_user.id))
    if not token:
        await message.answer(
            "Не вижу активного подтверждения. Вернитесь на сайт Руми и нажмите "
            "«Подтвердить в Telegram» — затем снова поделитесь контактом.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    record = await r.hgetall(_key(token))
    verdict = check_contact(
        record,
        message.contact.user_id,
        message.from_user.id,
        message.contact.phone_number,
    )

    if verdict == VERDICT_OK:
        await r.hset(_key(token), "status", TG_STATUS_CONFIRMED)
        await r.delete(_pending_key(message.from_user.id))
        logger.info(
            "confirmed: tg_user=%s phone=%s",
            message.from_user.id,
            _mask_phone(try_normalize_phone(message.contact.phone_number) or ""),
        )
        await message.answer(
            "Номер подтверждён ✅\nВернитесь на сайт — регистрация продолжится сама.",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif verdict == VERDICT_FOREIGN_CONTACT:
        await message.answer(
            "Это чужой контакт — так подтвердить номер нельзя. "
            "Нажмите кнопку «Поделиться контактом», чтобы отправить свой.",
            reply_markup=_CONTACT_KB,
        )
    elif verdict == VERDICT_PHONE_MISMATCH:
        await message.answer(
            "Этот Telegram привязан к другому номеру — не к тому, что указан "
            "при регистрации. Проверьте номер на сайте или подтвердите его "
            "с Telegram-аккаунта на этом номере.",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Подтверждение устарело (действует 10 минут). Вернитесь на сайт "
            "и начните заново.",
            reply_markup=ReplyKeyboardRemove(),
        )


async def main() -> None:
    if not settings.TG_BOT_TOKEN:
        # Не падаем: контейнер в compose поднимается вместе со стеком и до
        # появления токена просто спит (иначе restart: unless-stopped
        # устроил бы crash-loop). Дали токен → пересоздать контейнер.
        logger.warning(
            "TG_BOT_TOKEN не задан — бот в режиме ожидания. Задайте токен "
            "в .env и пересоздайте контейнер (up -d --force-recreate tg-bot)."
        )
        await asyncio.Event().wait()
        return

    bot = Bot(token=settings.TG_BOT_TOKEN)
    dp = Dispatcher()
    dp.message.register(on_start, CommandStart())
    dp.message.register(on_contact, F.contact)

    logger.info("Бот подтверждения номера запущен (long polling)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main())
