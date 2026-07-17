# app/web/pages/salon_detail.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from app.models.models import Salon, Master, Service, Promotion, User, Booking, BookingStatus, Review
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles
from app.services.loyalty_service import LoyaltyService
from app.services.schedule_utils import MAX_BOOKING_DAYS_AHEAD
from app.web.components.icons import (
    ICON_ARROW_LEFT,
    ICON_HEART,
    ICON_HEART_FILLED,
    ICON_MAP_PIN,
    ICON_PHONE,
    ICON_CLOCK,
)


async def render_salon_detail(db: AsyncSession, salon_id: int, user=None) -> str:
    result = await db.execute(select(Salon).where(Salon.id == salon_id))
    salon = result.scalar_one_or_none()

    if not salon:
        return """<!DOCTYPE html><html><body class="error-page"><div class="section-container-sm"><h1>Салон не найден</h1><a class="btn-primary" href="/salons">← Вернуться на главную</a></div></body></html>"""

    masters_result = await db.execute(
        select(Master).where(Master.salon_id == salon.id, Master.is_active == True)
    )
    masters = masters_result.scalars().all()

    promos_result = await db.execute(
        select(Promotion).where(Promotion.salon_id == salon.id, Promotion.is_active == True)
    )
    promotions = promos_result.scalars().all()

    # Лояльность видна клиенту заранее, до записи — скидку/бонусы даёт салон, не РУМИ.
    loyalty_html = ""
    if user:
        loyalty = await LoyaltyService.get_client_status(db, salon.id, user.id)
        chips = []
        if loyalty["is_regular_client"] and loyalty["regular_client_discount_percent"] > 0:
            chips.append(f'🏅 Постоянный клиент −{loyalty["regular_client_discount_percent"]}%')
        if loyalty["personal_discount_percent"]:
            chips.append(f'🎁 Ваша скидка −{loyalty["personal_discount_percent"]}%')
        if loyalty["bonus_points"] > 0:
            chips.append(f'⭐ {loyalty["bonus_points"]} баллов')
        if chips:
            loyalty_html = (
                '<div style="margin-top:0.75rem;display:flex;gap:0.75rem;flex-wrap:wrap">'
                + "".join(
                    f'<span class="badge" style="background:var(--color-accent-light);color:var(--color-primary)">{c}</span>'
                    for c in chips
                )
                + "</div>"
            )


    reviews_result = await db.execute(
        select(Review).where(Review.salon_id == salon.id).order_by(Review.created_at.desc()).limit(10)
    )
    reviews = reviews_result.scalars().all()

    heart_svg = ICON_HEART.replace('"', '&quot;')
    heart_filled_svg = ICON_HEART_FILLED.replace('"', '&quot;')
    star_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-star"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>'

    # ----- Верхний блок (салон) -----
    top_block = f"""
    <section class="salon-top-section">
        <div class="section-container">
            <a class="back-link" href="/salons/">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-arrow"><path d="m12 19-7-7 7-7"></path><path d="M19 12H5"></path></svg>
                Все салоны
            </a>
            <div class="salon-header-grid">
                <div class="salon-image-wrapper">
                    <img alt="{salon.name}" src="{salon.logo_url or '/static/images/default-salon.jpg'}">
                    <button class="favorite-btn top-fav-btn salon-top-fav" 
                            data-type="salon" 
                            data-id="{salon.id}" 
                            data-icon-heart="{heart_svg}"
                            data-icon-heart-filled="{heart_filled_svg}"
                            title="В избранное">
                        <span class="heart-icon">{ICON_HEART}</span>
                    </button>
                </div>
                <div class="salon-info-wrapper">
                    <h1 class="salon-title">{salon.name}</h1>
                    <div class="salon-meta">
                        <div class="salon-rating">
                            {star_svg}
                            <span class="rating-val">{salon.rating or 0.0:.1f}</span>
                            <span class="rating-count">({salon.reviews_count or 0} отзывов)</span>
                        </div>
                        <div class="salon-tags">
                            {_get_service_tags(salon)}
                        </div>
                    </div>
                    <p class="salon-desc">{salon.description or ''}</p>
                    <div class="salon-contacts">
                        <span class="contact-item">{ICON_MAP_PIN} {salon.address or 'Адрес не указан'}</span>
                        <span class="contact-item">{ICON_PHONE} {salon.phone or '—'}</span>
                        <span class="contact-item">{ICON_CLOCK} {salon.working_hours or 'Пн-Вс: 10:00 — 21:00'}</span>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """

    # ----- Акции -----
    promos_html = ""
    if promotions:
        promos_html = '<section class="section-container promos-section"><h2 class="section-title">Акции</h2><div class="promos-grid">'
        for p in promotions:
            promos_html += f"""
            <div class="promo-card">
                <span class="promo-badge">{p.tag}</span>
                <h3 class="promo-title">{p.title}</h3>
                <p class="promo-desc">{p.description or ''}</p>
            </div>
            """
        promos_html += '</div></section>'

    # ----- Мастера и запись -----
    masters_list_html = ""
    detail_html = ""

    for m in masters:
        user_result = await db.execute(select(User).where(User.id == m.user_id))
        master_user = user_result.scalar_one_or_none()
        user_name = master_user.full_name if master_user else "Мастер"
        avatar = master_user.avatar_url or ""

        # Карточка в списке
        masters_list_html += f"""
        <div class="master-card" data-master-id="{m.id}">
            <div class="master-image-box">
                {f'<img src="{avatar}" alt="{user_name}">' if avatar else f'<div class="master-avatar-placeholder">{user_name[0].upper()}</div>'}
            </div>
            <div class="master-info-box">
                <div>
                    <div class="master-name">{user_name}</div>
                    <div class="master-spec">{m.specialization or "Барбер"}</div>
                </div>
                <div class="master-stats">
                    <span>опыт: {m.experience_years} лет</span>
                    <span>⭐ {m.rating or 0.0:.1f}</span>
                </div>
                <button class="btn-primary master-book-btn" data-master-id="{m.id}">Записаться</button>
            </div>
        </div>
        """

        # Детальный вид
        services_result = await db.execute(select(Service).where(Service.master_id == m.id))
        services = services_result.scalars().all()

        services_html = ""
        for s in services:
            services_html += f"""
            <button class="service-btn" 
                    data-master-id="{m.id}"
                    data-service-id="{s.id}"
                    data-service-name="{s.name}"
                    data-price="{s.price}"
                    data-duration="{s.duration_minutes}">
                <div>
                    <div class="service-name">{s.name}</div>
                    <div class="service-duration">{s.duration_minutes} мин</div>
                </div>
                <div class="service-price">{s.price} ₽</div>
            </button>
            """

        detail_html += f"""
        <div class="master-detail hidden" data-master-id="{m.id}">
            <button class="back-to-masters">← Назад к мастерам</button>
            
            <div class="master-detail-profile">
                <div class="master-detail-avatar">
                    {f'<img src="{avatar}" alt="{user_name}">' if avatar else f'<div class="master-avatar-placeholder">{user_name[0].upper()}</div>'}
                </div>
                <div>
                    <div class="master-detail-name">{user_name}</div>
                    <div class="master-spec">{m.specialization or "Барбер"}</div>
                    <div class="master-stats">
                        <span>опыт: {m.experience_years} лет</span>
                        <span>⭐ {m.rating or 0.0:.1f}</span>
                    </div>
                </div>
                <div class="form-group">
                    <label>Комментарий:</label>
                    <textarea name="comment" rows="3" placeholder="Расскажите о вашем впечатлении..." style="width:100%;padding:0.75rem;border:1px solid var(--color-border);border-radius:0.5rem;resize:vertical"></textarea>
                </div>
                <button type="submit" class="btn-primary">Отправить отзыв</button>
            </form>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{salon.name} — руми</title>
    {get_base_styles()}
    <style>
        .salon-hero {{ background: linear-gradient(135deg, #FFF8F6, #F8C8DC33); padding: 3rem 0; margin-bottom: 2rem; }}
        .salon-hero h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .salon-hero .meta {{ display: flex; gap: 1.5rem; color: var(--color-muted); font-size: 0.9rem; flex-wrap:wrap; align-items:center }}
        .master-card {{ background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 1rem; padding: 1.5rem; margin-bottom: 1.25rem; transition: border-color 0.2s; }}
        .master-card:hover {{ border-color: var(--color-primary); }}
        .master-header {{ display: flex; gap: 1rem; align-items: start; margin-bottom: 1rem; }}
        .master-avatar {{ width: 4rem; height: 4rem; border-radius: 50%; background: linear-gradient(135deg, var(--color-primary), var(--color-accent)); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white; font-weight: 700; flex-shrink: 0; }}
        .master-info h3 {{ font-size: 1.1rem; margin-bottom: 0.25rem; }}
        .master-spec {{ font-size: 0.85rem; color: var(--color-muted); }}
        .services-section {{ border-top: 1px solid var(--color-border); padding-top: 1rem; margin-top: 0.5rem; }}
        .services-title {{ font-size: 0.85rem; font-weight: 600; color: var(--color-muted); margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.03em; }}
        .services-grid {{ display: flex; flex-direction: column; gap: 0.5rem; }}
        .service-card {{ display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.75rem; background: var(--color-surface-alt); border-radius: 0.75rem; transition: all 0.2s; }}
        .service-card:hover {{ background: var(--color-accent-light); }}
        .service-card.selected {{ background: var(--color-accent-light); border: 1px solid var(--color-primary); }}
        .service-info {{ flex: 1; }}
        .service-name {{ font-weight: 600; font-size: 0.95rem; color: var(--color-heading); }}
        .service-meta {{ font-size: 0.8rem; color: var(--color-muted); margin-top: 0.15rem; }}
        .service-price {{ font-weight: 700; font-size: 1.1rem; color: var(--color-primary); white-space: nowrap; }}
        .slots-container {{ border-top: 1px solid var(--color-primary); margin-top: 1rem; padding-top: 1rem; }}
        .slots-title {{ font-weight: 600; margin-bottom: 0.75rem; color: var(--color-heading); }}
        .slot-grid {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }}
        .slot-btn {{ padding: 0.5rem 0.75rem; border: 1px solid var(--color-primary); border-radius: 0.5rem; font-size: 0.85rem; cursor: pointer; background: white; color: var(--color-primary); transition: all 0.2s; font-weight: 500; }}
        .slot-btn:hover {{ background: var(--color-primary); color: white; }}
        .slot-btn.selected {{ background: var(--color-primary); color: white; }}
        .no-slots {{ color: var(--color-muted); font-size: 0.85rem; padding: 0.5rem 0; }}
        .book-panel {{ position: fixed; bottom: 0; left: 0; right: 0; background: white; border-top: 2px solid var(--color-primary); padding: 1rem 2rem; display: none; z-index: 200; box-shadow: 0 -4px 20px rgba(0,0,0,0.1); }}
        .book-panel.active {{ display: block; }}
        .book-panel-inner {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }}
        .promo-card {{ background: var(--color-surface-alt); border: 1px solid var(--color-border); border-radius: 0.75rem; padding: 1rem; margin-bottom: 0.5rem; }}
        .promo-tag {{ display: inline-block; background: linear-gradient(135deg, var(--color-primary), var(--color-accent)); color: white; padding: 0.15rem 0.5rem; border-radius: 1rem; font-size: 0.7rem; font-weight: 600; margin-right: 0.5rem; }}
        .section-title {{ font-size: 1.5rem; margin: 2rem 0 1rem; }}
        .review-card {{ background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 0.75rem; padding: 1rem; margin-bottom: 0.75rem; }}
        .review-header {{ display: flex; gap: 0.75rem; align-items: center; margin-bottom: 0.5rem; }}
        .review-stars {{ font-size: 0.9rem; }}
        .review-date {{ font-size: 0.8rem; color: var(--color-muted); margin-left: auto; }}
        .review-comment {{ color: var(--color-body); font-size: 0.9rem; }}
        .review-form-card {{ background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 1rem; padding: 1.5rem; margin-top: 2rem; }}
        .review-form-card h3 {{ margin-bottom: 1rem; }}
        .form-group {{ margin-bottom: 1rem; }}
        .form-group label {{ display: block; font-weight: 500; margin-bottom: 0.5rem; }}
        .rating-input {{ display: flex; gap: 0.5rem; }}
        .rating-input input {{ display: none; }}
        .rating-input label {{ font-size: 1.5rem; cursor: pointer; opacity: 0.5; transition: opacity 0.2s; }}
        .rating-input input:checked ~ label,
        .rating-input label:hover,
        .rating-input label:hover ~ label {{ opacity: 1; }}
        .fav-btn {{
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.2rem;
            transition: transform 0.2s;
            padding: 0.2rem;
        }}
        .fav-btn:hover {{
            transform: scale(1.2);
        }}
        .fav-btn.liked {{
            color: #ef4444;
        }}
    </style>
</head>
<body>
    {render_header("salons")}
    {render_sidebar("salons", user)}
    
    <main style="margin-right: 16rem;">
        <div class="salon-hero">
            <div class="section-container">
                <a href="/salons" style="color:var(--color-primary);text-decoration:none;margin-bottom:1rem;display:inline-block">← Все салоны</a>
                <h1 class="text-display">{salon.name}</h1>
                <div class="meta">
                    <span>📍 {salon.address or 'Адрес не указан'}</span>
                    <span>📞 {salon.phone or '—'}</span>
                    <span>⭐ {salon.rating} ({salon.reviews_count} отзывов)</span>
                    <button id="fav-salon-{salon.id}" onclick="toggleFavorite('salon', {salon.id})" class="fav-btn" title="Добавить в избранное">🤍</button>
                </div>
                {loyalty_html}
                <p style="margin-top:0.75rem;color:var(--color-body)">{salon.description or ''}</p>
>>>>>>> origin/main
            </div>
        </div>
        """

    masters_block = f"""
    <section class="section-container masters-section">
        <div class="section-header">
            <h2 class="section-title">Выберите мастера</h2>
        </div>
        <div id="masters-list-container">
            <div class="masters-list">
                {masters_list_html or '<p>В салоне пока нет мастеров.</p>'}
            </div>
        </div>
        {detail_html}
    </section>
    """

    # Плавающая панель записи
    booking_panel = """
    <div class="booking-panel hidden" id="bookPanel">
        <div class="booking-panel-inner">
            <div class="booking-info">
                <span class="booking-master" id="panelMaster"></span>
                <span class="booking-dot"> · </span>
                <span class="booking-time" id="panelTime"></span>
            </div>
            <button class="btn-primary" onclick="confirmBooking()">Записаться</button>
        </div>
    </div>
    
    {render_footer()}
    
    <script>
        let selectedSlot = null;
        let selectedMasterId = null;
        let selectedServiceId = null;
        
        // === ИЗБРАННОЕ ===
        async function checkFavorites() {{
            try {{
                const response = await fetch('/api/v1/favorites/my');
                const data = await response.json();
                data.salon_ids.forEach(id => {{
                    const btn = document.getElementById('fav-salon-' + id);
                    if (btn) {{ btn.textContent = '❤️'; btn.classList.add('liked'); }}
                }});
                data.master_ids.forEach(id => {{
                    const btn = document.getElementById('fav-master-' + id);
                    if (btn) {{ btn.textContent = '❤️'; btn.classList.add('liked'); }}
                }});
            }} catch(e) {{}}
        }}
        
        async function toggleFavorite(type, id) {{
            const btn = document.getElementById('fav-' + type + '-' + id);
            const isLiked = btn.classList.contains('liked');
            
            try {{
                const response = await fetch(`/api/v1/favorites/toggle-${{type}}/${{id}}`, {{ method: 'POST' }});
                if (response.ok) {{
                    if (isLiked) {{
                        btn.textContent = '🤍';
                        btn.classList.remove('liked');
                    }} else {{
                        btn.textContent = '❤️';
                        btn.classList.add('liked');
                    }}
                }}
            }} catch(e) {{
                alert('Ошибка. Попробуйте позже.');
            }}
        }}
        
        checkFavorites();
        
        // === СЛОТЫ ===
        async function showSlots(btn, masterId, serviceId, serviceName, price, duration) {{
            document.querySelectorAll('.service-select-btn').forEach(b => b.textContent = 'Выбрать');
            document.querySelectorAll('.service-card').forEach(c => c.classList.remove('selected'));
            
            btn.textContent = '✓ Выбрано';
            btn.parentElement.classList.add('selected');
            
            selectedMasterId = masterId;
            selectedServiceId = serviceId;
            
            document.querySelectorAll('.slots-container').forEach(c => c.style.display = 'none');
            
            const slotsContainer = document.getElementById('slots-' + masterId);
            const slotsTitle = document.getElementById('slots-title-' + masterId);
            const slotGrid = document.getElementById('slot-grid-' + masterId);
            
            slotsTitle.innerHTML = `
                📅 Доступное время для «${{serviceName}}» (${{price}} ₽, ${{duration}} мин):
                <br><input type="date" id="datePicker-${{masterId}}" value="${{new Date().toISOString().split('T')[0]}}"
                    min="${{new Date().toISOString().split('T')[0]}}"
                    max="${{new Date(Date.now() + {MAX_BOOKING_DAYS_AHEAD} * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}}"
                    onchange="loadSlots(${{masterId}}, ${{serviceId}}, '${{serviceName}}', ${{price}}, ${{duration}})"
                    style="margin-top:0.5rem;padding:0.4rem;border:1px solid var(--color-border);border-radius:0.5rem">
                <span style="font-size:0.75rem;color:var(--color-muted)">Запись открыта на {MAX_BOOKING_DAYS_AHEAD} дней вперёд</span>
            `;
            slotGrid.innerHTML = '<p style="color:var(--color-muted);font-size:0.85rem">Выберите дату для загрузки слотов...</p>';
            slotsContainer.style.display = 'block';
            slotsContainer.scrollIntoView({{ behavior: 'smooth' }});
            
            loadSlots(masterId, serviceId, serviceName, price, duration);
        }}
        
        async function loadSlots(masterId, serviceId, serviceName, price, duration) {{
            const datePicker = document.getElementById('datePicker-' + masterId);
            const dateStr = datePicker ? datePicker.value : new Date().toISOString().split('T')[0];
            const slotGrid = document.getElementById('slot-grid-' + masterId);
            
            slotGrid.innerHTML = '<p style="color:var(--color-muted);font-size:0.85rem">Загружаем слоты...</p>';
            
            try {{
                const response = await fetch(`/api/v1/bookings/available/${{masterId}}?date=${{dateStr}}&service_id=${{serviceId}}`);
                const data = await response.json();
                
                if (data.slots && data.slots.length > 0) {{
                    const now = new Date();
                    const todayStr = new Date().toISOString().split('T')[0];
                    let slotsHtml = '';
                    for (const slot of data.slots) {{
                        const slotDate = new Date(slot);
                        if (dateStr === todayStr && slotDate < now) continue;
                        
                        const timeStr = slotDate.toTimeString().slice(0, 5);
                        const fullSlot = slotDate.getFullYear() + '-' + 
                            String(slotDate.getMonth() + 1).padStart(2, '0') + '-' + 
                            String(slotDate.getDate()).padStart(2, '0') + 'T' + 
                            String(slotDate.getHours()).padStart(2, '0') + ':' + 
                            String(slotDate.getMinutes()).padStart(2, '0');
                        
                        slotsHtml += `<span class="slot-btn" onclick="selectSlot(this, '${{fullSlot}}', ${{masterId}}, ${{serviceId}}, '${{serviceName}}', ${{price}})">${{timeStr}}</span>`;
                    }}
                    
                    if (slotsHtml) {{
                        slotGrid.innerHTML = slotsHtml;
                    }} else {{
                        slotGrid.innerHTML = '<p class="no-slots">Нет свободных окон на выбранную дату.</p>';
                    }}
                }} else {{
                    slotGrid.innerHTML = `<p class="no-slots">${{data.message || 'Нет свободных окон на эту дату.'}}</p>`;
                }}
            }} catch (err) {{
                slotGrid.innerHTML = '<p class="no-slots">Ошибка загрузки. Попробуйте позже.</p>';
            }}
        }}
        
        function selectSlot(el, time, masterId, serviceId, serviceName, price) {{
            document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
            el.classList.add('selected');
            selectedSlot = time;
            selectedMasterId = masterId;
            selectedServiceId = serviceId;
            document.getElementById('bookPanel').classList.add('active');
            document.getElementById('panelMaster').textContent = `${{serviceName}} · ${{price}} ₽`;
            document.getElementById('panelTime').textContent = time.replace('T', ' ');
        }}
        
        function confirmBooking() {{
            if (!selectedSlot || !selectedMasterId || !selectedServiceId) {{
                alert('Выберите услугу и время!');
                return;
            }}
            window.location.href = `/book?master_id=${{selectedMasterId}}&service_id=${{selectedServiceId}}&time=${{encodeURIComponent(selectedSlot)}}`;
        }}
    </script>
</body>
</html>"""
    return html

def _get_service_tags(salon: Salon) -> str:
    if not salon.description:
        return ''
    keywords = ["стрижка", "борода", "маникюр", "педикюр", "окрашивание", "укладка", "брови"]
    found = [kw.capitalize() for kw in keywords if kw in salon.description.lower()]
    if not found:
        return ''
    return ''.join(f'<span class="badge-tag">{kw}</span>' for kw in found[:3])