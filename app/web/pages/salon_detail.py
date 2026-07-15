# app/web/pages/salon_detail.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from app.models.models import Salon, Master, Service, Promotion, User, Booking, BookingStatus, Review
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles
from app.web.components.icons import (
    ICON_ARROW_LEFT,
    ICON_HEART,
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

    reviews_result = await db.execute(
        select(Review).where(Review.salon_id == salon.id).order_by(Review.created_at.desc()).limit(10)
    )
    reviews = reviews_result.scalars().all()

    heart_svg = ICON_HEART.replace('"', '&quot;')
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
                    <button class="fav-btn top-fav-btn salon-top-fav" data-type="salon" data-id="{salon.id}" data-icon-heart="{heart_svg}">
                        <span class="heart-wrapper">{ICON_HEART}</span>
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

    # ----- НОВАЯ ВЕРСИЯ: Мастера и запись (как в образце) -----
    masters_list_html = ""
    detail_html = ""

    for m in masters:
        user_result = await db.execute(select(User).where(User.id == m.user_id))
        master_user = user_result.scalar_one_or_none()
        user_name = master_user.full_name if master_user else "Мастер"
        avatar = master_user.avatar_url or ""

        # Карточка мастера (отображается в списке)
        master_card = f"""
        <div class="master-card" data-master-id="{m.id}">
            <div class="master-layout">
                <div class="master-image-box">
                    {f'<img alt="{user_name}" src="{avatar}">' if avatar else f'<div class="master-avatar-placeholder">{user_name[0].upper()}</div>'}
                    <button class="fav-btn master-fav" data-type="master" data-id="{m.id}" data-icon-heart="{heart_svg}">
                        <span class="heart-wrapper">{ICON_HEART}</span>
                    </button>
                </div>
                <div class="master-info-box">
                    <div>
                        <h3 class="master-name">{user_name}</h3>
                        <p class="master-spec">{m.specialization}</p>
                    </div>
                    <div class="master-stats">
                        <span class="stat-item">опыт: {m.experience_years} лет</span>
                        <span class="stat-item rating-stat">
                            {star_svg}
                            <span class="rating-val">{m.rating}</span>
                        </span>
                    </div>
                    <button class="btn-primary master-book-btn" data-master-id="{m.id}">Записаться</button>
                </div>
            </div>
        </div>
        """
        masters_list_html += master_card

        # Детальный вид мастера (скрыт по умолчанию)
        services_result = await db.execute(
            select(Service).where(Service.master_id == m.id).order_by(Service.price)
        )
        services = services_result.scalars().all()

        services_list = ""
        for srv in services:
            services_list += f"""
            <button class="service-btn" 
                    data-master-id="{m.id}" 
                    data-service-id="{srv.id}"
                    data-service-name="{srv.name}"
                    data-price="{srv.price}"
                    data-duration="{srv.duration_minutes}">
                <span class="service-name">{srv.name}</span>
                <span class="service-duration">{srv.duration_minutes} мин</span>
                <span class="service-price">{srv.price} ₽</span>
            </button>
            """

        detail_html += f"""
        <div class="master-detail hidden" data-master-id="{m.id}">
            <div class="master-detail-header">
                <button class="btn-outline back-to-masters">← Назад к мастерам</button>
            </div>
            <div class="master-detail-profile">
                <div class="master-detail-avatar">
                    {f'<img alt="{user_name}" src="{avatar}">' if avatar else f'<div class="master-avatar-placeholder">{user_name[0].upper()}</div>'}
                </div>
                <div class="master-detail-info">
                    <h2 class="master-detail-name">{user_name}</h2>
                    <p class="master-detail-spec">{m.specialization}</p>
                    <div class="master-detail-stats">
                        <span>опыт: {m.experience_years} лет</span>
                        <span>⭐ {m.rating}</span>
                    </div>
                </div>
            </div>
            <div class="master-detail-services">
                <h3 class="services-title">Выберите услугу:</h3>
                <div class="services-grid">
                    {services_list}
                </div>
            </div>
            <!-- Слоты (появляются после выбора услуги) -->
            <div class="slots-container hidden" id="detail-slots-{m.id}">
                <div class="slots-title" id="detail-slots-title-{m.id}"></div>
                <div class="slots-grid" id="detail-slot-grid-{m.id}"></div>
            </div>
        </div>
        """

    # Если мастеров нет – показываем заглушку
    if not masters:
        masters_list_html = '<p class="empty-state">В этом салоне пока нет мастеров.</p>'
        detail_html = ""

    masters_block = f"""
    <section class="section-container masters-section">
        <div class="section-header">
            <span class="section-title">Выберите мастера</span>
        </div>
        <div id="masters-list-container">
            <div class="masters-list">
                {masters_list_html}
            </div>
        </div>
        <div id="master-detail-container">
            {detail_html}
        </div>
    </section>
    """

    # ----- Отзывы -----
    reviews_html = ""
    if reviews:
        for r in reviews:
            client_result = await db.execute(select(User).where(User.id == r.client_id))
            client_user = client_result.scalar_one_or_none()
            client_name = client_user.full_name if client_user else "Клиент"
            stars = "★" * r.rating + "☆" * (5 - r.rating)
            date_str = r.created_at.strftime("%d.%m.%Y") if r.created_at else ""
            reviews_html += f"""
            <div class="review-item">
                <div class="review-header">
                    <strong class="review-author">{client_name}</strong>
                    <span class="review-date">{date_str}</span>
                </div>
                <div class="review-stars">{stars}</div>
                <p class="review-text">{r.comment or 'Без комментария'}</p>
            </div>
            """
    else:
        reviews_html = '<p class="empty-state">Пока нет отзывов. Будьте первым!</p>'

    review_form = ""
    if user:
        masters_options = ""
        for m in masters:
            master_user = (await db.execute(select(User).where(User.id == m.user_id))).scalar_one_or_none()
            master_name = master_user.full_name if master_user else "Мастер"
            masters_options += f'<option value="{m.id}">{master_name} — {m.specialization}</option>'

        review_form = f"""
        <div class="review-form-container">
            <h3 class="form-title">Оставить отзыв</h3>
            <form action="/api/v1/reviews/create" method="post" class="review-form">
                <input type="hidden" name="salon_id" value="{salon.id}">
                <div class="form-group">
                    <label>Мастер:</label>
                    <select name="master_id" required class="form-control">
                        <option value="">Выберите мастера</option>
                        {masters_options}
                    </select>
                </div>
                <div class="form-group">
                    <label>Оценка:</label>
                    <div class="star-rating-input">
                        <input type="radio" name="rating" value="5" id="star5" class="hidden"><label for="star5">★</label>
                        <input type="radio" name="rating" value="4" id="star4" class="hidden"><label for="star4">★</label>
                        <input type="radio" name="rating" value="3" id="star3" class="hidden"><label for="star3">★</label>
                        <input type="radio" name="rating" value="2" id="star2" class="hidden"><label for="star2">★</label>
                        <input type="radio" name="rating" value="1" id="star1" required class="hidden"><label for="star1">★</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Комментарий:</label>
                    <textarea name="comment" rows="3" placeholder="Расскажите о вашем впечатлении..." class="form-control"></textarea>
                </div>
                <button type="submit" class="btn-primary submit-btn">Отправить отзыв</button>
            </form>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="ru" data-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{salon.name} | руми</title>
    {get_base_styles()}
    <link rel="stylesheet" href="/static/css/pages/salon_detail.css">
</head>
<body class="page-body">
    {render_header("salons")}
    {render_sidebar("salons", user)}

    <div class="main-wrapper">
        <main>
            {top_block}
            {promos_html}
            {masters_block}

            <section class="section-container reviews-section">
                <h2 class="section-title">Отзывы</h2>
                <div class="reviews-list">
                    {reviews_html}
                </div>
                {review_form}
            </section>

            {render_footer()}
        </main>
    </div>

    <div class="booking-panel hidden" id="bookPanel">
        <div class="booking-panel-inner">
            <div class="booking-info">
                <strong class="booking-master" id="panelMaster"></strong> 
                <span class="booking-dot">·</span> 
                <span class="booking-time" id="panelTime"></span>
            </div>
            <button class="btn-primary" onclick="confirmBooking()">Записаться</button>
        </div>
    </div>

    <script src="/static/js/pages/salon_detail.js"></script>
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