# app/web/pages/business/tabs/records.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.models.models import Booking, BookingStatus, Service as ServiceModel, User as UserModel

STATUS_LABELS = {
    BookingStatus.PENDING: ("Ожидает", "#f59e0b"),
    BookingStatus.CONFIRMED: ("Подтверждена", "#3b82f6"),
    BookingStatus.COMPLETED: ("Завершена", "#22c55e"),
    BookingStatus.CANCELLED: ("Отменена", "#9ca3af"),
    BookingStatus.NO_SHOW: ("Неявка", "#ef4444"),
}


async def render_records_tab(db: AsyncSession, salon, masters, master_ids, filters: dict) -> str:
    """Вкладка «Записи» — полный список броней салона с фильтрами.
    filters: {master_id, status, date_from, date_to} — все опциональны,
    приходят строками из query-параметров дашборда (см. views.py/dashboard.py)."""

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    default_from = today - timedelta(days=30)
    default_to = today + timedelta(days=1)

    def parse_date(value, fallback):
        if not value:
            return fallback
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return fallback

    date_from = parse_date(filters.get("date_from"), default_from)
    date_to = parse_date(filters.get("date_to"), default_to - timedelta(days=1)) + timedelta(days=1)
    filter_master_id = filters.get("master_id") or ""
    filter_status = filters.get("status") or ""

    rows_data = []
    if master_ids:
        query = (
            select(Booking, ServiceModel)
            .join(ServiceModel, ServiceModel.id == Booking.service_id)
            .where(
                Booking.master_id.in_(master_ids),
                Booking.start_time >= date_from,
                Booking.start_time < date_to,
            )
        )
        if filter_master_id.isdigit():
            query = query.where(Booking.master_id == int(filter_master_id))
        if filter_status:
            try:
                query = query.where(Booking.status == BookingStatus(filter_status))
            except ValueError:
                pass
        result = await db.execute(query.order_by(Booking.start_time.desc()).limit(200))
        rows_data = result.all()

    master_by_id = {m.id: m for m in masters}
    master_user_names = {}
    for m in masters:
        mu = (await db.execute(select(UserModel).where(UserModel.id == m.user_id))).scalar_one_or_none()
        master_user_names[m.id] = mu.full_name if mu else "—"

    client_ids = {b.client_id for b, s in rows_data}
    clients_by_id = {}
    for cid in client_ids:
        cu = (await db.execute(select(UserModel).where(UserModel.id == cid))).scalar_one_or_none()
        clients_by_id[cid] = cu.full_name or cu.phone if cu else "—"

    rows_html = ""
    for b, s in rows_data:
        label, color = STATUS_LABELS.get(b.status, (b.status.value, "#9ca3af"))
        price = f"{(b.final_price or s.price):,}".replace(",", " ")
        needs_badge = b.status == BookingStatus.COMPLETED and not b.consumption_reported
        badge = (
            '<span style="background:#FEF3C7;color:#92400E;border-radius:1rem;padding:0.125rem 0.6rem;'
            'font-size:0.7rem;font-weight:600;margin-left:0.5rem">не списано</span>'
            if needs_badge else ""
        )
        rows_html += f"""
        <tr>
            <td>{b.start_time.strftime('%d.%m.%Y %H:%M')}</td>
            <td>{clients_by_id.get(b.client_id, '—')}</td>
            <td>{master_user_names.get(b.master_id, '—')}</td>
            <td>{s.name}</td>
            <td><span style="color:{color};font-weight:600">{label}</span>{badge}</td>
            <td>{price} ₽</td>
        </tr>"""

    master_options = "".join(
        f'<option value="{m.id}"{" selected" if filter_master_id == str(m.id) else ""}>{master_user_names.get(m.id, "—")}</option>'
        for m in masters
    )
    status_options = "".join(
        f'<option value="{st.value}"{" selected" if filter_status == st.value else ""}>{label}</option>'
        for st, (label, _color) in STATUS_LABELS.items()
    )

    return f"""
    <div id="tab-records" class="tab-content">
        <form method="get" action="/business/dashboard" style="display:flex;gap:0.75rem;flex-wrap:wrap;align-items:flex-end;margin-bottom:1.5rem">
            <input type="hidden" name="salon_id" value="{salon.id}">
            <input type="hidden" name="tab" value="records">
            <div>
                <label class="text-muted" style="display:block;font-size:0.75rem;margin-bottom:0.25rem">С даты</label>
                <input type="date" name="date_from" value="{date_from.strftime('%Y-%m-%d')}" style="padding:0.5rem;border:1px solid var(--color-border);border-radius:0.5rem">
            </div>
            <div>
                <label class="text-muted" style="display:block;font-size:0.75rem;margin-bottom:0.25rem">По дату</label>
                <input type="date" name="date_to" value="{(date_to - timedelta(days=1)).strftime('%Y-%m-%d')}" style="padding:0.5rem;border:1px solid var(--color-border);border-radius:0.5rem">
            </div>
            <div>
                <label class="text-muted" style="display:block;font-size:0.75rem;margin-bottom:0.25rem">Мастер</label>
                <select name="master_id" style="padding:0.5rem;border:1px solid var(--color-border);border-radius:0.5rem">
                    <option value="">Все мастера</option>
                    {master_options}
                </select>
            </div>
            <div>
                <label class="text-muted" style="display:block;font-size:0.75rem;margin-bottom:0.25rem">Статус</label>
                <select name="status" style="padding:0.5rem;border:1px solid var(--color-border);border-radius:0.5rem">
                    <option value="">Все статусы</option>
                    {status_options}
                </select>
            </div>
            <button type="submit" class="btn-outline">Применить</button>
        </form>

        <div class="card" style="overflow-x:auto">
            <table>
                <thead>
                    <tr><th>Дата</th><th>Клиент</th><th>Мастер</th><th>Услуга</th><th>Статус</th><th>Сумма</th></tr>
                </thead>
                <tbody>
                    {rows_html or '<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--color-muted)">Записей за период нет</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>"""
