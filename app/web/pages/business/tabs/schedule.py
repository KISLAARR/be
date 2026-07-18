# app/web/pages/business/tabs/schedule.py
from collections import OrderedDict
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Booking, Master, Service, User as UserModel, BookingStatus, ScheduleClosure
from app.services.schedule_utils import get_salon_work_hours, MAX_BOOKING_DAYS_AHEAD
from app.services.schedule_service import ScheduleService

MONTH_NAMES_RU = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
]
WEEKDAY_NAMES_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


async def render_schedule_tab(
    db: AsyncSession, salon, masters, can_manage_schedule: bool = False,
    schedule_master_id: int = None, can_close_dates: bool = None,
) -> str:
    """Вкладка «Расписание»: выбор мастера → месяц → неделя → сетка
    дни×часы на MAX_BOOKING_DAYS_AHEAD (2 месяца) вперёд, плюс закрытие дат.

    can_manage_schedule — можно отмечать записи выполненными/неявкой (владелец/
    админ салона, либо сам мастер — на своих записях это уже разрешено бэкендом
    независимо от SalonMember). can_close_dates по умолчанию равен
    can_manage_schedule (владелец/админ), но у мастера, просматривающего только
    свой календарь, эти права разные: закрытие дат требует SalonMember,
    которого у мастера нет, поэтому вызывающий код передаёт False явно."""
    if can_close_dates is None:
        can_close_dates = can_manage_schedule

    if not masters:
        return ('<div id="tab-schedule" class="tab-content"><div class="card" '
                'style="padding:2rem;text-align:center;color:var(--color-muted)">В салоне пока нет мастеров</div></div>')

    master_by_id = {m.id: m for m in masters}
    selected_master = master_by_id.get(schedule_master_id) or masters[0]

    master_names = {}
    for m in masters:
        mu = (await db.execute(select(UserModel).where(UserModel.id == m.user_id))).scalar_one_or_none()
        master_names[m.id] = mu.full_name if mu else "—"

    today = datetime.now().date()
    days = [today + timedelta(days=i) for i in range(MAX_BOOKING_DAYS_AHEAD)]
    window_start = datetime.combine(today, datetime.min.time())
    window_end = window_start + timedelta(days=MAX_BOOKING_DAYS_AHEAD)

    # Закрытия, которые касаются выбранного мастера (свои + весь салон) в пределах окна — одним запросом
    closures_result = await db.execute(
        select(ScheduleClosure).where(
            ScheduleClosure.salon_id == salon.id,
            ScheduleClosure.date >= today,
            ScheduleClosure.date < today + timedelta(days=MAX_BOOKING_DAYS_AHEAD),
            (ScheduleClosure.master_id.is_(None)) | (ScheduleClosure.master_id == selected_master.id),
        )
    )
    closures_by_date = {}
    for c in closures_result.scalars().all():
        # Личное закрытие мастера показываем вместо общесалонного, если оба есть на одну дату
        if c.date not in closures_by_date or c.master_id is not None:
            closures_by_date[c.date] = c

    # Записи выбранного мастера на все 60 дней — одним запросом (без N+1 по дням)
    bookings_result = await db.execute(
        select(Booking).where(
            Booking.master_id == selected_master.id,
            Booking.start_time >= window_start,
            Booking.start_time < window_end,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
        ).order_by(Booking.start_time)
    )
    bookings = bookings_result.scalars().all()
    bookings_by_date = {}
    for b in bookings:
        bookings_by_date.setdefault(b.start_time.date(), []).append(b)

    # Подгружаем услуги/клиентов, встречающихся в записях, одним запросом на каждое
    service_ids = {b.service_id for b in bookings}
    client_ids = {b.client_id for b in bookings}
    services_by_id = {s.id: s for s in (
        (await db.execute(select(Service).where(Service.id.in_(service_ids)))).scalars().all() if service_ids else []
    )}
    clients_by_id = {u.id: u for u in (
        (await db.execute(select(UserModel).where(UserModel.id.in_(client_ids)))).scalars().all() if client_ids else []
    )}

    # Часы работы по дню недели — чистая функция, без БД; закрытая дата обнуляет часы независимо от графика
    weekly_hours_cache = {}
    day_hours = {}
    min_hour = max_hour = None
    for d in days:
        weekday = d.weekday()
        if weekday not in weekly_hours_cache:
            weekly_hours_cache[weekday] = get_salon_work_hours(salon.working_hours, datetime.combine(d, datetime.min.time()))
        hours = None if d in closures_by_date else weekly_hours_cache[weekday]
        day_hours[d] = hours
        if hours:
            s, e = hours
            min_hour = s.hour if min_hour is None else min(min_hour, s.hour)
            eh = e.hour + (1 if e.minute else 0)
            max_hour = eh if max_hour is None else max(max_hour, eh)

    row_hours = list(range(min_hour, max_hour)) if min_hour is not None else []

    def booking_cell_html(b) -> str:
        svc = services_by_id.get(b.service_id)
        client = clients_by_id.get(b.client_id)
        status = "confirmed" if b.status == BookingStatus.CONFIRMED else "pending"
        bg = "#dcfce7" if status == "confirmed" else "#fef9c3"
        actions = ""
        if can_manage_schedule and status == "confirmed":
            actions = f"""<div style="display:flex;gap:0.15rem;margin-top:0.15rem">
                <button onclick="event.stopPropagation();openCompleteModal({b.id}, {b.client_id})" title="Выполнено" style="border:none;background:#22c55e;color:white;border-radius:0.2rem;font-size:0.6rem;padding:0.1rem 0.25rem;cursor:pointer">✓</button>
                <button onclick="event.stopPropagation();markBooking({b.id}, 'no-show')" title="Неявка" style="border:none;background:#ef4444;color:white;border-radius:0.2rem;font-size:0.6rem;padding:0.1rem 0.25rem;cursor:pointer">✕</button>
            </div>"""
        svc_name = svc.name if svc else "—"
        client_name = client.full_name if client else "Клиент"
        time_str = f"{b.start_time.strftime('%H:%M')}-{b.end_time.strftime('%H:%M')}"
        return f"""<div style="background:{bg};padding:0.2rem 0.4rem;border-radius:0.25rem;margin-bottom:0.15rem;font-size:0.65rem" title="{client_name} — {svc_name} ({time_str})">
            {time_str}<br>{svc_name[:14]}{actions}
        </div>"""

    def build_week_grid(week_days) -> str:
        day_headers = ""
        day_cols = {h: "" for h in row_hours}
        for d in week_days:
            is_today = d == today
            header_style = "background:var(--color-accent-light)" if is_today else ""
            closure = closures_by_date.get(d)
            hours = day_hours[d]
            if closure:
                mark = "🚫 закрыто" if closure.master_id is None else "🚫 личное"
                closed_label = f'<div style="font-size:0.65rem;color:#ef4444">{mark}</div>'
            elif hours is None:
                closed_label = '<div style="font-size:0.65rem;color:var(--color-muted)">выходной</div>'
            else:
                closed_label = ""
            day_headers += (
                f'<th style="text-align:center;font-size:0.75rem;padding:0.4rem;min-width:110px;{header_style}">'
                f'{WEEKDAY_NAMES_RU[d.weekday()]} {d.strftime("%d.%m")}{closed_label}</th>'
            )
            for h in row_hours:
                within_hours = bool(hours) and hours[0].hour <= h < (hours[1].hour + (1 if hours[1].minute else 0))
                slot_start = datetime.combine(d, datetime.min.time()).replace(hour=h)
                slot_end = slot_start + timedelta(hours=1)
                content = "".join(
                    booking_cell_html(b) for b in bookings_by_date.get(d, [])
                    if b.start_time < slot_end and b.end_time > slot_start
                )
                cell_bg = "" if within_hours else "background:repeating-linear-gradient(45deg,#f3f4f6,#f3f4f6 6px,#fafafa 6px,#fafafa 12px)"
                day_cols[h] += f'<td style="padding:0.2rem;vertical-align:top;{cell_bg}">{content}</td>'

        rows_html = "".join(
            f'<tr><td style="font-size:0.75rem;color:var(--color-muted);padding:0.3rem;white-space:nowrap">{h}:00</td>{day_cols[h]}</tr>'
            for h in row_hours
        )
        return f'<table><thead><tr><th></th>{day_headers}</tr></thead><tbody>{rows_html}</tbody></table>'

    # Группируем 60 дней по (год, месяц), внутри — по неделям пн-старт (края могут быть неполными)
    months = OrderedDict()
    for d in days:
        months.setdefault((d.year, d.month), []).append(d)

    def split_weeks(month_days):
        weeks, cur = [], []
        for d in month_days:
            if cur and d.weekday() == 0:
                weeks.append(cur)
                cur = []
            cur.append(d)
        if cur:
            weeks.append(cur)
        return weeks

    if not row_hours:
        calendar_html = ('<div class="card" style="padding:2rem;text-align:center;color:var(--color-muted)">'
                          'У салона не задан рабочий график — нечего показывать</div>')
    else:
        month_tabs = ""
        month_panels = ""
        for mi, ((year, month), month_days) in enumerate(months.items()):
            month_key = f"{year}-{month:02d}"
            weeks = split_weeks(month_days)

            week_tabs = ""
            week_panels = ""
            for wi, week_days in enumerate(weeks):
                week_id = f"{month_key}-w{wi}"
                label = f"{week_days[0].strftime('%d.%m')}–{week_days[-1].strftime('%d.%m')}"
                active_week = " active" if wi == 0 else ""
                week_tabs += (
                    f'<button class="week-tab-btn{active_week}" data-month="{month_key}" data-week="{week_id}" '
                    f'onclick="showWeek(\'{month_key}\',\'{week_id}\')">{label}</button>'
                )
                active_panel = " active" if wi == 0 else ""
                week_panels += (
                    f'<div class="week-panel{active_panel}" id="week-{week_id}" data-month="{month_key}" '
                    f'style="overflow-x:auto">{build_week_grid(week_days)}</div>'
                )

            active_month = " active" if mi == 0 else ""
            month_tabs += f'<button class="month-tab-btn{active_month}" data-month="{month_key}" onclick="showMonth(\'{month_key}\')">{MONTH_NAMES_RU[month - 1]} {year}</button>'
            month_panels += f"""
            <div class="month-panel{active_month}" id="month-{month_key}">
                <div style="display:flex;gap:0.4rem;margin-bottom:0.75rem;flex-wrap:wrap">{week_tabs}</div>
                {week_panels}
            </div>"""

        calendar_html = f"""
        <div class="card">
            <div style="display:flex;gap:0.4rem;margin-bottom:1rem;flex-wrap:wrap;border-bottom:1px solid var(--color-border);padding-bottom:0.75rem">
                {month_tabs}
            </div>
            {month_panels}
        </div>"""

    master_select_options = "".join(
        f'<option value="{m.id}"{" selected" if m.id == selected_master.id else ""}>{master_names.get(m.id, "—")} — {m.specialization}</option>'
        for m in masters
    )

    # Закрытие дат — отдельное право от отметки записей (см. docstring)
    closures_section = ""
    if can_close_dates:
        upcoming_closures = await ScheduleService.list_closures(db, salon.id)
        closures_html = ""
        for c in upcoming_closures:
            scope = master_names.get(c.master_id, f"Мастер #{c.master_id}") if c.master_id else "Весь салон"
            reason_html = f' — {c.reason}' if c.reason else ''
            closures_html += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid var(--color-border);font-size:0.85rem">
                <span>📅 {c.date.strftime('%d.%m.%Y')} — {scope}{reason_html}</span>
                <button onclick="reopenClosure({c.id})" class="btn-outline" style="font-size:0.75rem;padding:0.25rem 0.6rem">Открыть</button>
            </div>"""

        closure_master_options = "".join(f'<option value="{m.id}">{master_names.get(m.id, "—")}</option>' for m in masters)

        closures_section = f"""
        <div class="card" style="margin-top:1.5rem">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
                <h3 style="font-size:1rem">🚫 Закрытые даты</h3>
                <button class="btn-primary" style="font-size:0.85rem;padding:0.5rem 1rem" onclick="document.getElementById('closeDateModal').classList.add('active')">+ Закрыть дату</button>
            </div>
            {closures_html or '<p class="text-muted" style="font-size:0.85rem">Ближайших закрытий нет</p>'}
        </div>

        <div class="modal-overlay" id="closeDateModal">
            <div class="modal-box">
                <button class="modal-close" onclick="document.getElementById('closeDateModal').classList.remove('active')">&times;</button>
                <h2 style="margin-bottom:1.5rem">Закрыть дату</h2>
                <div style="margin-bottom:1rem">
                    <label style="display:block;font-weight:500;margin-bottom:0.5rem">Дата *</label>
                    <input type="date" id="closeDateInput" required style="width:100%;padding:0.75rem;border:1px solid var(--color-border);border-radius:0.5rem">
                </div>
                <div style="margin-bottom:1rem">
                    <label style="display:block;font-weight:500;margin-bottom:0.5rem">Кто закрывается</label>
                    <select id="closeDateMaster" style="width:100%;padding:0.75rem;border:1px solid var(--color-border);border-radius:0.5rem">
                        <option value="">Весь салон</option>
                        {closure_master_options}
                    </select>
                </div>
                <div style="margin-bottom:1rem">
                    <label style="display:block;font-weight:500;margin-bottom:0.5rem">Причина</label>
                    <input type="text" id="closeDateReason" placeholder="Праздник, ремонт, отпуск…" style="width:100%;padding:0.75rem;border:1px solid var(--color-border);border-radius:0.5rem">
                </div>
                <button type="button" class="btn-primary" style="width:100%" onclick="submitCloseDate({salon.id})">Закрыть дату</button>
            </div>
        </div>"""

    return f"""
    <div id="tab-schedule" class="tab-content">
        <div style="margin-bottom:1rem">
            <select onchange="window.location.href='/business/dashboard?tab=schedule&salon_id={salon.id}&schedule_master_id=' + this.value"
                    style="padding:0.5rem 0.75rem;border:1px solid var(--color-border);border-radius:0.5rem;font-size:0.85rem;min-width:220px">
                {master_select_options}
            </select>
        </div>

        {calendar_html}

        <div style="display:flex;gap:1rem;margin-top:0.75rem;font-size:0.75rem;color:var(--color-muted);flex-wrap:wrap">
            <span><span style="display:inline-block;width:12px;height:12px;background:#dcfce7;border-radius:2px;margin-right:0.25rem"></span> Подтверждено</span>
            <span><span style="display:inline-block;width:12px;height:12px;background:#fef9c3;border-radius:2px;margin-right:0.25rem"></span> Ожидает</span>
            <span><span style="display:inline-block;width:12px;height:12px;background:repeating-linear-gradient(45deg,#f3f4f6,#f3f4f6 3px,#fafafa 3px,#fafafa 6px);border-radius:2px;margin-right:0.25rem"></span> Вне графика/закрыто</span>
        </div>

        {closures_section}
    </div>

    <style>
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }}
        .modal-overlay.active {{ display: flex; }}
        .modal-box {{
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            max-width: 500px;
            width: 90%;
            position: relative;
            max-height: 90vh;
            overflow-y: auto;
        }}
        .modal-close {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--color-muted);
        }}
        .modal-close:hover {{ color: var(--color-heading); }}

        .month-panel, .week-panel {{ display: none; }}
        .month-panel.active, .week-panel.active {{ display: block; }}
        .month-tab-btn, .week-tab-btn {{
            border: 1px solid var(--color-border);
            background: white;
            color: var(--color-heading);
            padding: 0.4rem 0.9rem;
            border-radius: 2rem;
            font-size: 0.8rem;
            cursor: pointer;
            white-space: nowrap;
        }}
        .month-tab-btn.active, .week-tab-btn.active {{
            background: var(--color-primary);
            border-color: var(--color-primary);
            color: white;
        }}
        #tab-schedule table {{ border-collapse: collapse; width: 100%; }}
        #tab-schedule th, #tab-schedule td {{ border-bottom: 1px solid var(--color-border); }}
    </style>

    <!-- Модалка завершения записи со скидкой лояльности (только у того, кто видит кнопку ✓ — т.е. у админа) -->
    <div class="modal-overlay" id="completeBookingModal">
        <div class="modal-box">
            <button class="modal-close" onclick="document.getElementById('completeBookingModal').classList.remove('active')">&times;</button>
            <h2 style="margin-bottom:1rem">Завершить запись</h2>
            <div id="completeModalBody" style="font-size:0.9rem">Загрузка…</div>
            <button type="button" class="btn-primary" style="width:100%;margin-top:1rem" onclick="submitCompleteWithDiscount()">Подтвердить</button>
        </div>
    </div>

    <script>
        function showMonth(monthKey) {{
            document.querySelectorAll('.month-panel').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.month-tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById('month-' + monthKey).classList.add('active');
            const btn = document.querySelector(`.month-tab-btn[data-month="${{monthKey}}"]`);
            if (btn) btn.classList.add('active');
        }}

        function showWeek(monthKey, weekId) {{
            document.querySelectorAll(`.week-panel[data-month="${{monthKey}}"]`).forEach(el => el.classList.remove('active'));
            document.querySelectorAll(`.week-tab-btn[data-month="${{monthKey}}"]`).forEach(el => el.classList.remove('active'));
            document.getElementById('week-' + weekId).classList.add('active');
            const btn = document.querySelector(`.week-tab-btn[data-month="${{monthKey}}"][data-week="${{weekId}}"]`);
            if (btn) btn.classList.add('active');
        }}

        function markBooking(bookingId, action) {{
            const label = action === 'complete' ? 'выполненной' : 'неявкой';
            if (!confirm(`Отметить запись ${{label}}?`)) return;
            fetch(`/api/v1/bookings/${{bookingId}}/${{action}}`, {{ method: 'POST' }})
                .then(r => {{ if (r.ok) location.reload(); else r.json().then(d => alert(d.detail || 'Ошибка')); }});
        }}

        let completeModalBookingId = null;

        async function openCompleteModal(bookingId, clientId) {{
            completeModalBookingId = bookingId;
            const body = document.getElementById('completeModalBody');
            body.innerHTML = 'Загрузка…';
            document.getElementById('completeBookingModal').classList.add('active');

            let status;
            try {{
                const res = await fetch(`/api/v1/loyalty/salon/{salon.id}/client/${{clientId}}`);
                status = await res.json();
            }} catch (e) {{
                body.innerHTML = 'Не удалось загрузить скидки клиента. Можно завершить без скидки.';
                status = {{ offers: [], bonus_points: 0 }};
            }}

            let html = '<label style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.5rem;cursor:pointer">'
                + '<input type="radio" name="discountChoice" value="none" checked> Без скидки</label>';

            if (status.is_regular_client && status.regular_client_discount_percent > 0) {{
                html += `<label style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.5rem;cursor:pointer">
                    <input type="radio" name="discountChoice" value="regular_client"> Постоянный клиент (-${{status.regular_client_discount_percent}}%)</label>`;
            }}
            if (status.personal_discount_percent) {{
                html += `<label style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.5rem;cursor:pointer">
                    <input type="radio" name="discountChoice" value="personal"> Персональная скидка (-${{status.personal_discount_percent}}%)</label>`;
            }}
            (status.offers || []).forEach(o => {{
                if (!o.promo_code) return;
                html += `<label style="display:flex;gap:0.5rem;align-items:center;margin-bottom:0.5rem;cursor:pointer">
                    <input type="radio" name="discountChoice" value="promo" data-code="${{o.promo_code}}"> ${{o.title}} (-${{o.discount_percent}}%, промокод ${{o.promo_code}})</label>`;
            }});

            html += `<div style="margin-top:0.75rem">
                <label style="display:block;font-weight:500;margin-bottom:0.25rem">Списать баллов (доступно: ${{status.bonus_points || 0}})</label>
                <input type="number" id="completeBonusPoints" min="0" max="${{status.bonus_points || 0}}" value="0" style="width:100%;padding:0.5rem;border:1px solid var(--color-border);border-radius:0.5rem">
            </div>`;

            body.innerHTML = html;
        }}

        async function submitCompleteWithDiscount() {{
            const selected = document.querySelector('input[name="discountChoice"]:checked');
            const discount_choice = selected ? selected.value : 'none';
            const promo_code = selected && selected.dataset.code ? selected.dataset.code : null;
            const bonusEl = document.getElementById('completeBonusPoints');
            const bonus_points_redeemed = bonusEl ? (parseInt(bonusEl.value) || 0) : 0;

            const res = await fetch(`/api/v1/bookings/${{completeModalBookingId}}/complete`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ discount_choice, promo_code, bonus_points_redeemed }})
            }});
            if (res.ok) {{ location.reload(); }}
            else {{ const d = await res.json(); alert(d.detail || 'Ошибка'); }}
        }}

        async function submitCloseDate(salonId) {{
            const date = document.getElementById('closeDateInput').value;
            const masterId = document.getElementById('closeDateMaster').value;
            const reason = document.getElementById('closeDateReason').value;
            if (!date) {{ alert('Укажите дату'); return; }}
            const res = await fetch(`/api/v1/schedule/salon/${{salonId}}/closures`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ date, master_id: masterId ? parseInt(masterId) : null, reason: reason || null }})
            }});
            if (res.ok) {{ location.reload(); }}
            else {{ const d = await res.json(); alert(d.detail || 'Ошибка'); }}
        }}

        function reopenClosure(closureId) {{
            if (!confirm('Открыть эту дату снова для записи?')) return;
            fetch(`/api/v1/schedule/salon/{salon.id}/closures/${{closureId}}`, {{ method: 'DELETE' }})
                .then(async r => {{ if (r.ok) location.reload(); else {{ const d = await r.json(); alert(d.detail || 'Ошибка'); }} }});
        }}
    </script>"""
