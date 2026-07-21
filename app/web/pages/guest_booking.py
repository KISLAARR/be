# app/web/pages/guest_booking.py
"""Публичные страницы записи без регистрации: /book/{salon_id} и /guest-booking/{token}."""
import json

from sqlalchemy import select

from app.models.models import (
    Salon, Master, Service, User, Booking, Master as _M,
    SalonModerationStatus, BookingStatus,
)
from app.web.components.styles import get_base_styles


def _shell(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} — Руми</title>
    {get_base_styles()}
</head>
<body>
    <main style="max-width:640px;margin:0 auto;padding:1.5rem 1rem">
        {body}
    </main>
</body>
</html>"""


def _notice(title: str, text: str) -> str:
    return _shell(title, f"""
        <div style="text-align:center;padding:3rem 1rem">
            <h1 style="margin-bottom:0.5rem">{title}</h1>
            <p class="text-muted">{text}</p>
            <p style="margin-top:1.5rem"><a href="/" class="text-link">На главную Руми</a></p>
        </div>""")


async def render_guest_booking_page(db, salon_id: int) -> str:
    salon = (await db.execute(select(Salon).where(Salon.id == salon_id))).scalar_one_or_none()
    if (
        not salon
        or not salon.is_active
        or salon.moderation_status != SalonModerationStatus.APPROVED
        or not salon.guest_booking_enabled
    ):
        return _notice("Запись недоступна", "Этот салон сейчас не принимает записи без регистрации.")

    masters = (await db.execute(
        select(Master).where(Master.salon_id == salon_id, Master.is_active == True)
    )).scalars().all()

    data = []
    for m in masters:
        muser = (await db.execute(select(User).where(User.id == m.user_id))).scalar_one_or_none()
        services = (await db.execute(
            select(Service).where(Service.master_id == m.id, Service.is_active == True).order_by(Service.price)
        )).scalars().all()
        if not services:
            continue
        data.append({
            "id": m.id,
            "name": (muser.full_name if muser else None) or "Мастер",
            "spec": m.specialization or "",
            "services": [{"id": s.id, "name": s.name, "price": s.price, "duration": s.duration_minutes} for s in services],
        })

    if not data:
        return _notice("Пока нельзя записаться", "У салона нет доступных мастеров или услуг.")

    masters_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    body = f"""
        <h1 style="margin-bottom:0.25rem">Запись в «{salon.name}»</h1>
        <p class="text-muted" style="margin-bottom:1.5rem">Без регистрации — оставьте имя и телефон, салон подтвердит запись.</p>
        <div id="guest-book" data-salon-id="{salon.id}" data-masters='{masters_json}'>

            <div class="gb-step" data-step="master">
                <h2 class="gb-h2">1. Выберите мастера</h2>
                <div id="gb-masters" class="gb-list"></div>
            </div>

            <div class="gb-step" data-step="service" style="display:none">
                <button class="gb-back" data-to="master">← Мастера</button>
                <h2 class="gb-h2">2. Услуга</h2>
                <div id="gb-services" class="gb-list"></div>
            </div>

            <div class="gb-step" data-step="slot" style="display:none">
                <button class="gb-back" data-to="service">← Услуги</button>
                <h2 class="gb-h2">3. Дата и время</h2>
                <input type="date" id="gb-date" class="gb-input" style="margin-bottom:0.75rem">
                <div id="gb-slots" class="gb-slots"></div>
            </div>

            <div class="gb-step" data-step="details" style="display:none">
                <button class="gb-back" data-to="slot">← Время</button>
                <h2 class="gb-h2">4. Ваши данные</h2>
                <div id="gb-summary" class="text-muted" style="margin-bottom:0.75rem"></div>
                <div class="form-group"><label>Имя *</label>
                    <input type="text" id="gb-name" class="gb-input" required></div>
                <div class="form-group"><label>Телефон *</label>
                    <input type="tel" id="gb-phone" class="phone-input" placeholder="+7 (___) ___-__-__" required></div>
                <div class="form-group"><label>Email (для уведомлений, необязательно)</label>
                    <input type="email" id="gb-email" class="gb-input" placeholder="example@mail.ru"></div>
                <p id="gb-error" style="color:var(--color-danger,#c0392b);min-height:1.2em"></p>
                <button id="gb-submit" class="btn-primary" style="width:100%">Записаться</button>
            </div>

            <div class="gb-step" data-step="done" style="display:none">
                <div style="text-align:center;padding:1.5rem 0">
                    <h2 style="margin-bottom:0.5rem">Заявка отправлена ✅</h2>
                    <p class="text-muted">Салон подтвердит запись. Сохраните ссылку, чтобы посмотреть или отменить бронь:</p>
                    <p style="margin:1rem 0"><a id="gb-manage-link" href="#" class="text-link"></a></p>
                </div>
            </div>
        </div>
        <style>
        .gb-h2{{font-size:1.1rem;margin:0 0 0.75rem}}
        .gb-list{{display:flex;flex-direction:column;gap:0.5rem}}
        .gb-card{{text-align:left;padding:0.9rem 1rem;border:1px solid var(--color-border,#e0e0e0);border-radius:12px;background:var(--color-surface,#fff);cursor:pointer;width:100%}}
        .gb-card:hover{{border-color:var(--color-primary,#7c3aed)}}
        .gb-card small{{color:var(--color-muted,#888)}}
        .gb-slots{{display:grid;grid-template-columns:repeat(auto-fill,minmax(76px,1fr));gap:0.5rem}}
        .gb-slot{{padding:0.5rem;border:1px solid var(--color-border,#e0e0e0);border-radius:8px;background:var(--color-surface,#fff);cursor:pointer}}
        .gb-slot:hover{{border-color:var(--color-primary,#7c3aed)}}
        .gb-back{{background:none;border:none;color:var(--color-muted,#888);cursor:pointer;padding:0 0 0.75rem}}
        .gb-input{{width:100%;padding:0.6rem 0.75rem;border:1px solid var(--color-border,#e0e0e0);border-radius:8px;font-size:1rem;background:var(--color-surface,#fff)}}
        </style>"""
    return _shell(f"Запись в {salon.name}", body)


async def render_guest_manage_page(db, token: str) -> str:
    booking = (await db.execute(
        select(Booking).where(Booking.guest_manage_token == token)
    )).scalar_one_or_none()
    if not booking:
        return _notice("Бронь не найдена", "Ссылка недействительна или устарела.")

    service = (await db.execute(select(Service).where(Service.id == booking.service_id))).scalar_one_or_none()
    master = (await db.execute(select(Master).where(Master.id == booking.master_id))).scalar_one_or_none()
    muser = (await db.execute(select(User).where(User.id == master.user_id))).scalar_one_or_none() if master else None
    salon = (await db.execute(select(Salon).where(Salon.id == master.salon_id))).scalar_one_or_none() if master else None

    status_ru = {
        BookingStatus.PENDING: "Ожидает подтверждения салона",
        BookingStatus.CONFIRMED: "Подтверждена ✅",
        BookingStatus.COMPLETED: "Выполнена",
        BookingStatus.CANCELLED: "Отменена",
        BookingStatus.NO_SHOW: "Неявка",
    }.get(booking.status, str(booking.status))

    when = booking.start_time.strftime("%d.%m.%Y %H:%M") if booking.start_time else ""
    can_cancel = booking.status in (BookingStatus.PENDING, BookingStatus.CONFIRMED)
    cancel_btn = (
        f'<button id="gb-cancel" class="btn-outline" data-token="{token}" style="width:100%;margin-top:1rem">Отменить запись</button>'
        if can_cancel else ""
    )

    body = f"""
        <h1 style="margin-bottom:1rem">Ваша запись</h1>
        <div style="border:1px solid var(--color-border,#e0e0e0);border-radius:12px;padding:1.25rem">
            <p><strong>{salon.name if salon else ""}</strong></p>
            <p class="text-muted">{(muser.full_name if muser else "") or "Мастер"} · {service.name if service else ""}</p>
            <p style="margin-top:0.5rem">🗓 {when}</p>
            <p style="margin-top:0.5rem">Статус: <strong>{status_ru}</strong></p>
            {cancel_btn}
            <p id="gb-cancel-msg" style="min-height:1.2em;margin-top:0.5rem"></p>
        </div>
        <p style="margin-top:1.5rem;text-align:center"><a href="/" class="text-link">На главную Руми</a></p>"""
    return _shell("Ваша запись", body)
