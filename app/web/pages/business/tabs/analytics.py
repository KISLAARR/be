# app/web/pages/business/tabs/analytics.py
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from app.web.components.hint import hint as _hint
from app.models.models import Booking, Service, BookingStatus, User as UserModel
from app.web.components.icons import (
    ICON_RUBLE_SIGN,
    ICON_TRENDING_UP,
    ICON_STAR_FILLED,
    ICON_ARROW_UP_RIGHT,
    ICON_X,
    ICON_CLOCK,
)



async def render_analytics_tab(db: AsyncSession, salon, master_ids):
    """Вкладка Аналитика с графиком и топ-услугами."""
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    
    # Выручка по дням недели (текущая неделя)
    revenue_data = {}
    prev_revenue_data = {}
    week_operations = {}  # для деталей дня

    for i in range(7):
        # Текущая неделя
        day = today - timedelta(days=today.weekday()) + timedelta(days=i)
        day_end = day + timedelta(days=1)
        
        if master_ids:
            rev = await db.execute(
                select(func.coalesce(func.sum(Booking.final_price), 0))
                .where(
                    Booking.master_id.in_(master_ids),
                    Booking.start_time >= day,
                    Booking.start_time < day_end,
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                )
            )
            revenue_data[i] = rev.scalar() or 0
            
            # Операции за день (для деталей)
            ops = await db.execute(
                select(Booking, Service, UserModel)
                .join(Service, Service.id == Booking.service_id)
                .join(UserModel, UserModel.id == Booking.client_id)
                .where(
                    Booking.master_id.in_(master_ids),
                    Booking.start_time >= day,
                    Booking.start_time < day_end,
                    Booking.status != BookingStatus.CANCELLED
                )
                .order_by(Booking.start_time)
            )
            week_operations[i] = ops.all()
        else:
            revenue_data[i] = 0
            week_operations[i] = []

        # Прошлая неделя (только выручка)
        prev_day = today - timedelta(days=today.weekday() + 7) + timedelta(days=i)
        prev_day_end = prev_day + timedelta(days=1)
        if master_ids:
            prev_rev = await db.execute(
                select(func.coalesce(func.sum(Booking.final_price), 0))
                .where(
                    Booking.master_id.in_(master_ids),
                    Booking.start_time >= prev_day,
                    Booking.start_time < prev_day_end,
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                )
            )
            prev_revenue_data[i] = prev_rev.scalar() or 0
        else:
            prev_revenue_data[i] = 0

    total_revenue = sum(revenue_data.values())
    prev_total_revenue = sum(prev_revenue_data.values())
    revenue_diff = total_revenue - prev_total_revenue
    revenue_trend = "▲" if revenue_diff > 0 else "▼" if revenue_diff < 0 else "—"
    revenue_color = "#22c55e" if revenue_diff > 0 else "#ef4444" if revenue_diff < 0 else "var(--color-muted)"

    # Считаем общее количество записей за неделю (все статусы) и оплачиваемых
    # (подтверждённые/завершённые — для среднего чека, чтобы отменённые не занижали его)
    week_total = 0
    week_paid_total = 0
    for i in range(7):
        day = today - timedelta(days=today.weekday()) + timedelta(days=i)
        day_end = day + timedelta(days=1)
        if master_ids:
            cnt = await db.execute(select(func.count(Booking.id)).where(
                Booking.master_id.in_(master_ids),
                Booking.start_time >= day,
                Booking.start_time < day_end
            ))
            week_total += cnt.scalar() or 0

            paid_cnt = await db.execute(select(func.count(Booking.id)).where(
                Booking.master_id.in_(master_ids),
                Booking.start_time >= day,
                Booking.start_time < day_end,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
            ))
            week_paid_total += paid_cnt.scalar() or 0

    # Топ услуг
    top_services = []
    if master_ids:
        top_svc = await db.execute(
            select(Service.name, func.count(Booking.id).label("cnt"), func.sum(Booking.final_price).label("total"))
            .join(Booking, Booking.service_id == Service.id)
            .where(Booking.master_id.in_(master_ids), Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]))
            .group_by(Service.name)
            .order_by(func.sum(Booking.final_price).desc())
            .limit(5)
        )
        top_services = top_svc.all()

    top_services_rows = ""
    for name, cnt, total in top_services:
        total_val = f"{total or 0}".replace(",", " ")
        cnt_val = f"{cnt}".replace(",", " ")
        top_services_rows += f"""
        <tr>
            <td>{name}</td>
            <td>{cnt_val}</td>
            <td><strong>{total_val} ₽</strong></td>
        </tr>"""

    # Подготовка данных для JS (аккордеон)
    week_ops_serialized = []
    for i in range(7):
        day_ops = []
        for booking, service, client in week_operations[i]:
            day_ops.append({
                "id": booking.id,
                "start_time": booking.start_time.isoformat(),
                "final_price": booking.final_price,
                "status": booking.status.value,
                "payment_method": getattr(booking, "payment_method", "Карта"),
                "service": {"name": service.name, "price": service.price},
                "client": {"full_name": client.full_name, "phone": client.phone}
            })
        week_ops_serialized.append(day_ops)
    week_operations_json = json.dumps(week_ops_serialized, ensure_ascii=False)
    days_json = json.dumps(days, ensure_ascii=False)

    # График выручки (макс высота 100px)
    max_revenue = max(max(revenue_data.values()) if revenue_data else 1, 1)
    chart_height = 100
    revenue_bars = ""
    for i in range(7):
        height = int(revenue_data[i] / max_revenue * chart_height) if max_revenue > 0 else 5
        height = max(height, 8)  # минимальная видимая высота
        is_highest = revenue_data[i] == max(revenue_data.values()) if revenue_data else False
        rev_val = f"{revenue_data[i]}".replace(",", " ")
        bar_color = "#059669" if is_highest else "#34d399"
        bar_bg = f"background: linear-gradient(to top, {bar_color}, {bar_color}cc);"
        revenue_bars += f"""
        <div class="chart-column" data-day-index="{i}" onclick="showDayDetails({i}, '{days[i]}', {revenue_data[i]}, {prev_revenue_data[i]})" style="cursor:pointer">
            <div class="chart-value">{rev_val} ₽</div>
            <div class="chart-fill {'highest' if is_highest else ''}" style="height:{height}px; {bar_bg}"></div>
            <span class="chart-label">{days[i]}</span>
        </div>"""

    # Аккордеон для деталей дня
    accordion_html = f"""
    <div class="day-accordion" id="dayAccordion" style="display:none;">
        <div class="day-accordion-header">
            <h4 id="accordionDayTitle">Операции за день</h4>
            <span id="accordionDaySummary" class="text-muted"></span>
            <button class="accordion-close">{ICON_X}</button>
        </div>
        <div id="accordionDayOperations" class="day-accordion-body"></div>
    </div>
    """

    return f"""
    <div id="tab-analytics" class="tab-content">
        <div class="analytics-kpi">
            <div class="kpi-card">
                <div class="kpi-label">Выручка за неделю {_hint("Сумма подтверждённых и завершённых записей за текущую неделю (Пн—Вс).")}</div>
                <div class="kpi-value">{total_revenue:,} ₽</div>
                <div class="kpi-trend" style="color:{revenue_color}">{revenue_trend} {abs(revenue_diff):,} ₽ vs прошлая</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Средний чек {_hint("Выручка за неделю, делённая на число подтверждённых и завершённых записей (отменённые и ожидающие в расчёт не входят).")}</div>
                <div class="kpi-value">{total_revenue // max(week_paid_total, 1):,} ₽</div>
                <div class="kpi-trend" style="color:var(--color-muted)">за неделю</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Всего записей {_hint("Все записи за неделю к мастерам салона — включая отменённые и ещё не подтверждённые.")}</div>
                <div class="kpi-value">{week_total}</div>
                <div class="kpi-trend" style="color:var(--color-muted)">за неделю</div>
            </div>
        </div>

        <div class="card" style="margin-bottom:1.5rem">
            <h3 style="margin-bottom:0.5rem">{ICON_TRENDING_UP} Выручка по дням {_hint("Столбики — выручка по подтверждённым/завершённым записям каждого дня: сплошной — эта неделя, бледный — прошлая, для сравнения.")}</h3>
            <div class="legend">
                <span><span class="legend-dot" style="background:linear-gradient(to top,var(--color-primary),var(--color-accent))"></span> Эта неделя</span>
                <span><span class="legend-dot" style="background:var(--color-border)"></span> Прошлая неделя</span>
            </div>
            <div class="chart-bar">{revenue_bars}</div>
            <p style="font-size:0.75rem;color:var(--color-muted);text-align:center;margin-top:0.5rem">Нажмите на столбец, чтобы увидеть детали</p>
            
            {accordion_html}
        </div>
        
        <div class="card">
            <h3 style="margin-bottom:1rem">{ICON_STAR_FILLED} Топ услуг по выручке {_hint("Топ-5 услуг за всё время (не только за неделю) по сумме подтверждённых и завершённых записей.")}</h3>
            <table>
                <thead>
                    <tr><th>Услуга</th><th>Записей</th><th>Выручка</th></tr>
                </thead>
                <tbody>
                    {top_services_rows or '<tr><td colspan="3" style="text-align:center;padding:2rem;color:var(--color-muted)">Нет данных</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        window.analyticsWeekOperations = {week_operations_json};
        window.analyticsDays = {days_json};
    </script>
    """