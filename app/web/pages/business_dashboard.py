# app/web/pages/business_dashboard.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from app.models.models import Salon, Master, Service, Promotion, Booking, User as UserModel
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles


async def render_business_dashboard(db: AsyncSession, user, salon: Salon) -> str:
    """Улучшенная бизнес-панель с реальной аналитикой."""
    
    # === РЕАЛЬНАЯ СТАТИСТИКА ===
    
    # Мастера
    masters_result = await db.execute(select(Master).where(Master.salon_id == salon.id))
    masters = masters_result.scalars().all()
    
    # Услуги
    master_ids = [m.id for m in masters]
    services_count = 0
    if master_ids:
        svc = await db.execute(select(func.count(Service.id)).where(Service.master_id.in_(master_ids)))
        services_count = svc.scalar() or 0
    
    # Акции
    promos_result = await db.execute(select(Promotion).where(Promotion.salon_id == salon.id))
    promotions = promos_result.scalars().all()
    
    # Записи за сегодня
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    today_bookings = 0
    if master_ids:
        tb = await db.execute(select(func.count(Booking.id)).where(Booking.master_id.in_(master_ids), Booking.start_time >= today, Booking.start_time < tomorrow))
        today_bookings = tb.scalar() or 0
    
    # Записи за неделю (для графика)
    week_data = {}
    for i in range(7):
        day = today - timedelta(days=today.weekday()) + timedelta(days=i)
        day_end = day + timedelta(days=1)
        if master_ids:
            count = await db.execute(select(func.count(Booking.id)).where(Booking.master_id.in_(master_ids), Booking.start_time >= day, Booking.start_time < day_end))
            week_data[i] = count.scalar() or 0
        else:
            week_data[i] = 0
    
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    max_val = max(week_data.values()) if week_data else 1
    chart_bars = ""
    for i in range(7):
        height = int(week_data[i] / max_val * 160) if max_val > 0 else 5
        chart_bars += f'<div class="chart-column"><div class="chart-value">{week_data[i]}</div><div class="chart-fill" style="height:{max(height, 5)}px"></div><div class="chart-label">{days[i]}</div></div>'
    
    # Таблица мастеров (с явной загрузкой пользователя)
    masters_rows = ""
    for m in masters:
        # Явно загружаем пользователя вместо ленивой загрузки m.user
        user_result = await db.execute(
            select(UserModel).where(UserModel.id == m.user_id)
        )
        master_user = user_result.scalar_one_or_none()
        user_name = master_user.full_name if master_user else "—"
        
        # Явно считаем услуги мастера
        svc_result = await db.execute(
            select(func.count(Service.id)).where(Service.master_id == m.id)
        )
        svc_count = svc_result.scalar() or 0
        
        masters_rows += f"""
        <tr>
            <td>{user_name}</td>
            <td>{m.specialization}</td>
            <td>{m.experience_years} лет</td>
            <td>{svc_count}</td>
            <td>⭐ {m.rating}</td>
        </tr>
        """
    
    # Таблица акций
    promos_rows = ""
    for p in promotions:
        promos_rows += f"""
        <tr>
            <td>{p.title}</td>
            <td><span class="promo-badge">{p.tag}</span></td>
            <td>{p.description or '—'}</td>
        </tr>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Бизнес-панель — {salon.name} — руми</title>
    {get_base_styles()}
    <style>
        .tab-nav {{ display:flex; gap:0.25rem; border-bottom:1px solid var(--color-border); margin-bottom:2rem }}
        .tab-btn {{ padding:0.75rem 1.5rem; border:none; background:transparent; cursor:pointer; font-size:0.875rem; font-weight:500; color:var(--color-muted); border-bottom:2px solid transparent; transition:all 0.2s }}
        .tab-btn.active {{ color:var(--color-primary); border-bottom-color:var(--color-primary) }}
        .tab-content {{ display:none }}
        .tab-content.active {{ display:block }}
        .stat-card {{ background:var(--color-surface); border:1px solid var(--color-border); border-radius:1rem; padding:1.5rem; text-align:center }}
        .stat-value {{ font-size:2rem; font-weight:700; color:var(--color-primary) }}
        .stat-label {{ font-size:0.85rem; color:var(--color-muted); margin-top:0.25rem }}
        .promo-badge {{ display:inline-block; border-radius:2rem; padding:0.125rem 0.5rem; font-size:0.625rem; font-weight:700; color:white; background:linear-gradient(135deg,var(--color-primary),var(--color-accent)) }}
        table {{ width:100%; border-collapse:collapse }}
        th {{ text-align:left; padding:0.75rem; border-bottom:2px solid var(--color-border); font-weight:600; color:var(--color-heading) }}
        td {{ padding:0.75rem; border-bottom:1px solid var(--color-border) }}
        .chart-bar {{ height:200px; display:flex; align-items:flex-end; gap:1rem; padding:1rem 0 }}
        .chart-column {{ flex:1; display:flex; flex-direction:column; align-items:center; gap:0.5rem }}
        .chart-fill {{ width:100%; max-width:3rem; border-radius:0.5rem 0.5rem 0 0; background:linear-gradient(to top,var(--color-primary),var(--color-accent)); transition:height 0.3s }}
        .chart-label {{ font-size:0.75rem; color:var(--color-muted) }}
        .chart-value {{ font-size:0.7rem; font-weight:600; color:var(--color-heading) }}
    </style>
</head>
<body>
    {render_header("business", user)}
    {render_sidebar("business")}
    
    <main style="margin-right:16rem;padding-top:2rem">
        <div class="section-container">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
                <div>
                    <h1 class="text-display" style="font-size:2rem">{salon.name}</h1>
                    <p class="text-muted">Панель управления · ⭐ {salon.rating} ({salon.reviews_count} отзывов)</p>
                </div>
                <a href="/business/my-salon" class="btn-outline">✏️ Редактировать салон</a>
            </div>
            
            <!-- Вкладки -->
            <div class="tab-nav">
                <button class="tab-btn active" onclick="switchTab('overview')">📊 Обзор</button>
                <button class="tab-btn" onclick="switchTab('schedule')">📅 Расписание</button>
                <button class="tab-btn" onclick="switchTab('masters')">👥 Мастера ({len(masters)})</button>
                <button class="tab-btn" onclick="switchTab('promos')">🎉 Акции ({len(promotions)})</button>
            </div>
            
            <!-- Обзор -->
            <div id="tab-overview" class="tab-content active">
                <div class="grid-3" style="margin-bottom:2rem">
                    <div class="stat-card"><div class="stat-value">{len(masters)}</div><div class="stat-label">Мастеров</div></div>
                    <div class="stat-card"><div class="stat-value">{services_count}</div><div class="stat-label">Услуг</div></div>
                    <div class="stat-card"><div class="stat-value">{today_bookings}</div><div class="stat-label">Записей сегодня</div></div>
                    <div class="stat-card"><div class="stat-value">{len(promotions)}</div><div class="stat-label">Акций</div></div>
                    <div class="stat-card"><div class="stat-value">⭐ {salon.rating}</div><div class="stat-label">Рейтинг</div></div>
                    <div class="stat-card"><div class="stat-value">{salon.reviews_count}</div><div class="stat-label">Отзывов</div></div>
                </div>
                
                <!-- График записей за неделю -->
                <div class="card" style="margin-bottom:2rem">
                    <h3 style="margin-bottom:1rem">📊 Записи за неделю</h3>
                    <div class="chart-bar">{chart_bars}</div>
                </div>
            </div>
            
            <!-- Расписание (заглушка) -->
            <div id="tab-schedule" class="tab-content">
                <div class="card" style="text-align:center;padding:3rem">
                    <h3>📅 Управление расписанием</h3>
                    <p class="text-muted">Здесь будет календарь с записями по дням и мастерам</p>
                    <p class="text-muted" style="font-size:0.8rem">Функционал в разработке</p>
                </div>
            </div>
            
            <!-- Мастера -->
            <div id="tab-masters" class="tab-content">
                <div class="card" style="overflow-x:auto">
                    <table>
                        <thead>
                            <tr><th>Имя</th><th>Специализация</th><th>Опыт</th><th>Услуг</th><th>Рейтинг</th></tr>
                        </thead>
                        <tbody>
                            {masters_rows or '<tr><td colspan="5" style="text-align:center;padding:2rem;color:var(--color-muted)">Пока нет мастеров</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Акции -->
            <div id="tab-promos" class="tab-content">
                <div class="card" style="overflow-x:auto">
                    <table>
                        <thead>
                            <tr><th>Название</th><th>Тег</th><th>Описание</th></tr>
                        </thead>
                        <tbody>
                            {promos_rows or '<tr><td colspan="3" style="text-align:center;padding:2rem;color:var(--color-muted)">Пока нет акций</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>
    
    {render_footer()}
    
    <script>
        function switchTab(tabName) {{
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>"""
    
    return html