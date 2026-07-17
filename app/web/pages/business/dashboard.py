# app/web/pages/business/dashboard.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from app.models.models import (
    Salon, Master, Service, Promotion, Booking, Review, BookingStatus,
    SalonMember, User as UserModel,
)
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles
from app.web.components.icons import (
    ICON_LAYOUT_DASHBOARD,
    ICON_CLOCK,
    ICON_USERS,
    ICON_WALLET,
    ICON_PACKAGE,
    ICON_CHART_COLUMN,
    ICON_HEART,
    ICON_CALENDAR_DAYS,
    ICON_MESSAGE_CIRCLE,
    ICON_STAR_FILLED,
    ICON_BUILDING2,
    ICON_USER_CHECK,
    ICON_ARROW_UP_RIGHT,
    ICON_DOLLAR_SIGN,
    ICON_TRENDING_UP,
    ICON_SPARKLES,
)
from app.web.pages.business.utils import get_masters_data, get_master_ids
from app.web.pages.business.tabs.overview import render_overview_tab
from app.web.pages.business.tabs.analytics import render_analytics_tab
from app.web.pages.business.tabs.promos import render_promos_tab
from app.web.pages.business.tabs.reviews import render_reviews_tab
from app.web.pages.business.tabs.schedule import render_schedule_tab
from app.web.pages.business.tabs.employees import render_employees_tab
from app.web.pages.business.tabs.services import render_services_tab
from app.web.pages.business.tabs.records import render_records_tab
from app.web.pages.business.tabs.warehouse import render_warehouse_tab
from app.web.pages.business.tabs.payroll import render_payroll_tab
from app.web.pages.business.tabs.cost import render_cost_tab
from app.web.pages.business.tabs.promo_models import render_promo_models_tab
from app.web.pages.business.tabs.chat import render_chat_tab
from app.web.pages.business.tabs.staff import render_staff_tab
from app.crm.tabs.clients import render_crm_tab


async def render_business_dashboard(db: AsyncSession, user, salon: Salon, membership: SalonMember, query_params=None) -> str:
    """Бизнес-панель с аналитикой."""

    query_params = query_params or {}
    active_tab = query_params.get("tab", "overview")
    records_filters = {
        "date_from": query_params.get("date_from"),
        "date_to": query_params.get("date_to"),
        "master_id": query_params.get("master_id"),
        "status": query_params.get("status"),
    }
    warehouse_filters = {
        "audit_id": query_params.get("audit_id"),
    }
    period_raw = query_params.get("period")
    staff_notice = {
        "added": query_params.get("added"),
        "temp_pw": query_params.get("temp_pw"),
        "error": query_params.get("error"),
    }
    schedule_master_id_raw = query_params.get("schedule_master_id")
    schedule_master_id = int(schedule_master_id_raw) if schedule_master_id_raw and schedule_master_id_raw.isdigit() else None

    perms = {
        key: (membership.is_creator or membership.permissions.get(key, False))
        for key in (
            "manage_salon", "manage_owners", "manage_admins", "manage_masters",
            "manage_schedule", "manage_promotions", "manage_reviews",
            "view_finances", "manage_tariff", "view_audit_log",
            "manage_inventory", "manage_payroll",
        )
    }

    # Салоны, доступные пользователю — для свитчера в шапке
    other_memberships = (await db.execute(
        select(SalonMember, Salon)
        .join(Salon, Salon.id == SalonMember.salon_id)
        .where(SalonMember.user_id == user.id, SalonMember.is_active == True)
        .order_by(Salon.name)
    )).all()

    # Общие данные
    masters, masters_rows = await get_masters_data(db, salon.id)
    master_ids = get_master_ids(masters)

    services_count = 0
    if master_ids:
        svc = await db.execute(select(func.count(Service.id)).where(Service.master_id.in_(master_ids)))
        services_count = svc.scalar() or 0

    promos_result = await db.execute(select(Promotion).where(Promotion.salon_id == salon.id))
    promotions = promos_result.scalars().all()

    reviews_result = await db.execute(
        select(Review).where(Review.salon_id == salon.id).order_by(Review.created_at.desc())
    )
    reviews = reviews_result.scalars().all()

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    today_bookings = 0
    if master_ids:
        tb = await db.execute(select(func.count(Booking.id)).where(
            Booking.master_id.in_(master_ids),
            Booking.start_time >= today,
            Booking.start_time < tomorrow
        ))
        today_bookings = tb.scalar() or 0

    # Рендерим вкладки
    tabs_html = []
    tab_buttons = []

    # Обзор
    tab_buttons.append(('overview', ICON_LAYOUT_DASHBOARD, 'Обзор', True))
    tabs_html.append(await render_overview_tab(db, salon, masters, master_ids, services_count, promotions, today_bookings))

    # Аналитика (только с правом view_finances)
    tab_buttons.append(('analytics', ICON_CHART_COLUMN, 'Аналитика', perms["view_finances"]))
    if perms["view_finances"]:
        tabs_html.append(await render_analytics_tab(db, salon, master_ids))

    # Расписание
    tab_buttons.append(('schedule', ICON_CLOCK, 'Расписание', True))
    tabs_html.append(await render_schedule_tab(db, salon, masters, perms["manage_schedule"], schedule_master_id))

    # Мастера (сотрудники)
    tab_buttons.append(('employees', ICON_USERS, 'Сотрудники', True))
    tabs_html.append(await render_employees_tab(db, salon, masters))

    # Услуги
    tab_buttons.append(('services', ICON_USER_CHECK, 'Услуги', True))
    tabs_html.append(await render_services_tab(db, salon, masters))

    # Зарплаты (с правом manage_payroll)
    tab_buttons.append(('payroll', ICON_WALLET, 'Зарплаты', perms["manage_payroll"]))
    if perms["manage_payroll"]:
        tabs_html.append(await render_payroll_tab(db, salon, masters, master_ids, period_raw))

    # Себестоимость (с правом view_finances)
    tab_buttons.append(('cost', ICON_PACKAGE, 'Себестоимость', perms["view_finances"]))
    if perms["view_finances"]:
        tabs_html.append(await render_cost_tab(db, salon, masters, master_ids, period_raw))

    # Записи
    tab_buttons.append(('records', ICON_CALENDAR_DAYS, 'Записи', True))
    tabs_html.append(await render_records_tab(db, salon, masters, master_ids, records_filters))

    # Склад (с правом manage_inventory)
    tab_buttons.append(('warehouse', ICON_PACKAGE, 'Склад', perms["manage_inventory"]))
    if perms["manage_inventory"]:
        tabs_html.append(await render_warehouse_tab(db, salon, masters, master_ids, warehouse_filters))

    # Чат
    tab_buttons.append(('chat', ICON_MESSAGE_CIRCLE, 'Чат', True))
    tabs_html.append(await render_chat_tab(db, salon, user))

    # Сотрудники (админы/владельцы) – с правом manage_admins или manage_owners
    tab_buttons.append(('staff', ICON_USERS, 'Сотрудники', perms["manage_admins"] or perms["manage_owners"]))
    if perms["manage_admins"] or perms["manage_owners"]:
        tabs_html.append(await render_staff_tab(db, salon, user, membership, perms, staff_notice))

    # Модели (с правом manage_masters)
    tab_buttons.append(('models', ICON_HEART, 'Модели', perms["manage_masters"]))
    if perms["manage_masters"]:
        tabs_html.append(await render_promo_models_tab(db, salon))

    # Акции
    tab_buttons.append(('promos', ICON_SPARKLES, f'Акции ({len(promotions)})', True))
    tabs_html.append(render_promos_tab(promotions))

    # Отзывы
    tab_buttons.append(('reviews', ICON_STAR_FILLED, f'Отзывы ({len(reviews)})', True))
    tabs_html.append(await render_reviews_tab(db, reviews, salon))

    # CRM – Клиенты
    tab_buttons.append(('crm', ICON_USER_CHECK, 'Клиенты', True))
    tabs_html.append(await render_crm_tab(db, salon, masters, master_ids))

    visible_slugs = [slug for slug, _, _, visible in tab_buttons if visible]
    if active_tab not in visible_slugs:
        active_tab = "overview"

    nav_buttons_html = ""
    for slug, icon, label, visible in tab_buttons:
        if not visible:
            continue
        active_class = " active" if slug == active_tab else ""
        nav_buttons_html += f'<button class="tab-btn{active_class}" onclick="switchTab(\'{slug}\')">{icon} {label}</button>'

    tabs_body_html = "\n".join(tabs_html).replace(
        f'id="tab-{active_tab}" class="tab-content"',
        f'id="tab-{active_tab}" class="tab-content active"',
        1,
    )

    switcher_html = ""
    if len(other_memberships) > 1:
        options = "".join(
            f'<option value="{s.id}"{" selected" if s.id == salon.id else ""}>{s.name}</option>'
            for _, s in other_memberships
        )
        switcher_html = f"""
        <select onchange="window.location.href='/business/dashboard?salon_id=' + this.value" style="padding:0.5rem 0.75rem;border:1px solid var(--color-border);border-radius:0.5rem;font-size:0.85rem">
            {options}
        </select>"""

    # ===== ВЕРХНЯЯ ЧАСТЬ =====
    header_html = f"""
    <div class="dashboard-header">
        <div class="dashboard-header-inner">
            <div>
                <h1>Панель салона</h1>
                <p>Салон «{salon.name}» • {salon.address.split(',')[0] if salon.address else 'Адрес не указан'}</p>
            </div>
            <span class="dashboard-badge">
                {ICON_SPARKLES} Бизнес PRO
            </span>
        </div>
    </div>
    """

    # Основная разметка
    html = f"""<!DOCTYPE html>
<html lang="ru" class="dashboard-page">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Бизнес-панель — {salon.name} — руми</title>
    {get_base_styles()}
    <link rel="stylesheet" href="/static/src/css/business/dashboard.css">
</head>
<body>
    {render_header("business")}
    {render_sidebar("business_dashboard", user)}
    <main style="margin-right:0;padding-top:0">
        {header_html}

        <div class="section-container" style="padding-top: 1.5rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:0.75rem">
                <div>
                    <h1 class="text-display" style="font-size:1.5rem;margin:0">{salon.name}</h1>
                    <p class="text-muted" style="margin:0.25rem 0 0">⭐ {salon.rating} · {salon.reviews_count} отзывов</p>
                </div>
                <div style="display:flex;align-items:center;gap:0.75rem">
                    {switcher_html}
                    {f'<a href="/business/my-salon?salon_id={salon.id}" class="btn-outline">✏️ Редактировать салон</a>' if perms["manage_salon"] else ''}
                </div>
            </div>

            <div class="tab-nav">
                {nav_buttons_html}
            </div>

            {tabs_body_html}
        </div>
    </main>

    {render_footer(user)}

    <script src="/static/src/js/business/dashboard.js"></script>
</body>
</html>"""
    return html