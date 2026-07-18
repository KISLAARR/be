# tests/test_tg_notifications.py
"""Уведомления о записях в Telegram: ETA напоминания, ретраи отправки,
привязка chat_id при регистрации, постановка задач при создании записи."""
import asyncio
from datetime import datetime, timedelta, timezone

import httpx
import pytest
from arq import create_pool
from arq.worker import Worker
from zoneinfo import ZoneInfo

import app.services.notifications as notif
import app.services.otp as otp_mod
import app.tasks as tasks
from app.core.worker import REDIS_SETTINGS
from app.models.models import (
    Booking,
    BookingStatus,
    Master,
    Salon,
    SalonMember,
    SalonRole,
    Service,
    User,
    UserRole,
)
from app.services.otp import TG_STATUS_CONFIRMED, _hash, _key
from app.tg_bot import check_contact, VERDICT_OK

QUEUE = "test_queue_tg"
settings = otp_mod.settings


# ── reminder_eta_utc: таймзона салона учитывается ────────────────────────────

def test_reminder_eta_is_two_hours_before_in_salon_tz():
    start_local = datetime.now(ZoneInfo("Asia/Vladivostok")).replace(tzinfo=None) + timedelta(hours=10)
    eta = notif.reminder_eta_utc(start_local, "Asia/Vladivostok")
    expected = start_local.replace(tzinfo=ZoneInfo("Asia/Vladivostok")).astimezone(timezone.utc) - timedelta(hours=2)
    assert eta == expected


def test_reminder_eta_none_for_soon_or_past():
    soon = datetime.now(ZoneInfo("Europe/Moscow")).replace(tzinfo=None) + timedelta(minutes=30)
    assert notif.reminder_eta_utc(soon, "Europe/Moscow") is None
    past = datetime.now(ZoneInfo("Europe/Moscow")).replace(tzinfo=None) - timedelta(hours=1)
    assert notif.reminder_eta_utc(past, "Europe/Moscow") is None


# ── Задача отправки: ретраи на временных сбоях ──────────────────────────────

async def test_send_tg_message_retries_on_transient(monkeypatch):
    calls = {"n": 0}

    async def flaky(chat_id, text):
        calls["n"] += 1
        if calls["n"] < 3:
            raise tasks.TransientTaskError("Bot API 502")

    monkeypatch.setattr(tasks, "_send_via_telegram", flaky)
    monkeypatch.setattr(tasks, "RETRY_BASE_DELAY", 0)

    pool = await create_pool(REDIS_SETTINGS)
    try:
        job = await pool.enqueue_job("send_tg_message", 42, "тест", _queue_name=QUEUE)
        worker = Worker(
            functions=[tasks.send_tg_message],
            redis_settings=REDIS_SETTINGS,
            queue_name=QUEUE,
            max_tries=5,
            poll_delay=0.1,
            handle_signals=False,
        )
        wtask = asyncio.create_task(worker.async_run())
        try:
            result = await job.result(timeout=15)
        finally:
            await worker.close()
            wtask.cancel()
    finally:
        await pool.aclose()

    assert result == "sent"
    assert calls["n"] == 3


async def test_transport_maps_status_codes(monkeypatch):
    """5xx/429 → транзиентная ошибка (ретрай); 403 — постоянный отказ, молча."""
    # _send_via_telegram берёт settings импортом в момент вызова — патчим
    # АКТУАЛЬНЫЙ объект app.core.config.settings (test_config_guards мог
    # пересоздать модуль reload'ом, и наш module-level settings уже не тот)
    import app.core.config as config_mod
    monkeypatch.setattr(config_mod.settings, "TG_BOT_TOKEN", "000:x")

    def set_status(status_code):
        async def fake_post(self, url, json=None):
            return httpx.Response(status_code, request=httpx.Request("POST", url), text="{}")
        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    set_status(502)
    with pytest.raises(tasks.TransientTaskError):
        await tasks._send_via_telegram(1, "hi")
    set_status(429)
    with pytest.raises(tasks.TransientTaskError):
        await tasks._send_via_telegram(1, "hi")
    set_status(403)
    await tasks._send_via_telegram(1, "hi")  # не бросает — просто лог


# ── Привязка chat_id при регистрации через бота ─────────────────────────────

async def test_registration_saves_tg_chat_id(client, db_session, monkeypatch, tg_enabled=None):
    monkeypatch.setattr(settings, "TG_VERIFY_ENABLED", True)
    monkeypatch.setattr(settings, "TG_BOT_TOKEN", "000:x")
    monkeypatch.setattr(settings, "TG_BOT_USERNAME", "rumi_test_bot")

    phone = "+79995556677"
    r = await client.post("/api/v1/auth/register/tg-start", json={"phone": phone})
    request_id = r.json()["request_id"]

    # «Бот»: подтверждает и запоминает chat_id — ровно как app/tg_bot.py
    redis = otp_mod.get_redis()
    record = await redis.hgetall(_key(request_id))
    assert check_contact(record, 777, 777, "79995556677") == VERDICT_OK
    await redis.hset(_key(request_id), "status", TG_STATUS_CONFIRMED)
    await otp_mod.save_tg_chat_id(record["phone_hash"], 424242)

    r = await client.post(
        "/api/v1/auth/register-web",
        data={"phone": phone, "password": "Testpass1", "full_name": "ТГ",
              "request_id": request_id, "code": ""},
    )
    assert r.status_code == 302 and r.headers["location"] == "/profile"

    from sqlalchemy import select
    async with db_session() as db:
        user = (await db.execute(select(User).where(User.phone == phone))).scalar_one()
        assert user.tg_chat_id == 424242


# ── Постановка уведомлений при создании записи ──────────────────────────────

async def test_notify_booking_created_enqueues_for_all_parties(db_session, monkeypatch):
    monkeypatch.setattr(settings, "TG_NOTIFY_ENABLED", True)

    enqueued: list[tuple] = []

    class FakePool:
        async def enqueue_job(self, fn, *args, **kwargs):
            enqueued.append((fn, args, kwargs))

    async def fake_pool():
        return FakePool()

    monkeypatch.setattr(notif, "get_arq_pool", fake_pool)

    async with db_session() as db:
        owner = User(phone="+79990001001", hashed_password="x", role=UserRole.BUSINESS,
                     full_name="Владелец", tg_chat_id=111)
        master_user = User(phone="+79990001002", hashed_password="x", role=UserRole.MASTER,
                           full_name="Мастер", tg_chat_id=222)
        client_user = User(phone="+79990001003", hashed_password="x", role=UserRole.CLIENT,
                           full_name="Клиент", tg_chat_id=333)
        db.add_all([owner, master_user, client_user])
        await db.flush()

        salon = Salon(name="Тест-салон", address="ул. Тестовая, 1", timezone="Europe/Moscow",
                      creator_id=owner.id, latitude=55.75, longitude=37.62,
                      phone="+79990001000")
        db.add(salon)
        await db.flush()
        db.add(SalonMember(salon_id=salon.id, user_id=owner.id, role=SalonRole.OWNER,
                           is_creator=True, is_active=True, permissions={}))
        master = Master(user_id=master_user.id, salon_id=salon.id,
                        specialization="стрижка")
        db.add(master)
        await db.flush()
        service = Service(master_id=master.id, name="Стрижка", price=1000, duration_minutes=60)
        db.add(service)
        await db.flush()

        booking = Booking(
            client_id=client_user.id, master_id=master.id, service_id=service.id,
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=1),
            status=BookingStatus.PENDING, final_price=1000,
        )
        db.add(booking)
        await db.commit()
        await db.refresh(booking)

        await notif.notify_booking_created(db, booking)

    fns = [e[0] for e in enqueued]
    # мгновенные: владельцу (111), мастеру (222), клиенту (333)
    chat_ids = [e[1][0] for e in enqueued if e[0] == "send_tg_message"]
    assert sorted(chat_ids) == [111, 222, 333]
    # отложенное напоминание клиенту с дедуп-ключом
    reminders = [e for e in enqueued if e[0] == "send_booking_reminder"]
    assert len(reminders) == 1
    assert reminders[0][2]["_job_id"] == f"booking-reminder:{booking.id}"
    assert reminders[0][2]["_defer_until"] is not None
