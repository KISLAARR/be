# app/web/pages/home.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Salon
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles


async def render_home_page(db: AsyncSession, user=None) -> str:
    """Главная страница руми."""
    
    # Получаем популярные салоны
    try:
        result = await db.execute(
            select(Salon).where(Salon.is_active == True).order_by(Salon.rating.desc()).limit(3)
        )
        salons = result.scalars().all()
    except Exception as e:
        print(f"Ошибка загрузки салонов: {e}")
        salons = []
    
    # Карточки салонов
    salon_cards = ""
    for s in salons:
        salon_cards += f"""
        <div class="card salon-card">
            <div class="salon-avatar">{s.name[0]}</div>
            <h3 class="text-subtitle salon-name">{s.name}</h3>
            <p class="salon-address">📍 {s.address or 'Адрес не указан'}</p>
            <p class="salon-rating">
                ⭐ {s.rating or '0.0'} 
                <span class="salon-rating-count">({s.reviews_count or 0} отзывов)</span>
            </p>
            <a href="/salons/{s.id}" class="btn-primary salon-btn">Подробнее</a>
        </div>
        """
    
    if not salons:
        salon_cards = '<p class="salon-empty">Пока нет салонов. <a href="/register">Зарегистрируйтесь</a> как владелец, чтобы добавить первый салон!</p>'

    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Руми — мастера и салоны красоты рядом</title>
    <meta name="description" content="Платформа для клиентов и бизнеса: находите лучших мастеров, становитесь моделью или управляйте своим салоном.">
    {get_base_styles()}

</head>
<body>
    {render_header("home", user)}
    {render_sidebar("home")}

    <main class="home-main">
        <!-- Hero -->
        <section class="home-hero">
            <div class="section-container home-hero-content">
                <div class="badge" style="margin-bottom: 1rem;">Запись в пару кликов</div>
                <h1 class="text-display home-hero-title">Красота — рядом<br>с вами</h1>
                <p class="home-hero-subtitle">Выберите услугу, салон и время — готово. Никаких звонков, всё онлайн.</p>
                
                <a href="/salons" class="home-search-bar">
                    <div class="home-search-icon">🔍</div>
                    <div class="home-search-info">
                        <span class="home-search-title">Найти салон или услугу</span>
                        <span class="home-search-desc">Маникюр, стрижка, окрашивание, брови...</span>
                    </div>
                    <div class="home-search-btn">Найти</div>
                </a>
                
                <div class="home-hero-tags">
                    <a href="/salons" class="btn-outline" style="font-size: 0.85rem;">✂️ Стрижка</a>
                    <a href="/salons" class="btn-outline" style="font-size: 0.85rem;">💅 Маникюр</a>
                    <a href="/salons" class="btn-outline" style="font-size: 0.85rem;">🎨 Окрашивание</a>
                    <a href="/salons" class="btn-outline" style="font-size: 0.85rem;">✨ Брови</a>
                </div>
                
                <div class="home-hero-features">
                    <span class="home-feature-item">📍 Салоны рядом с вами</span>
                    <span class="home-feature-item">⚡ Запись за 30 секунд</span>
                    <span class="home-feature-item">✅ Проверенные мастера</span>
                </div>
            </div>
        </section>

        <!-- Как записаться -->
        <section class="section-py bg-surface">
            <div class="section-container">
                <div class="section-header">
                    <div class="badge">Просто как 1-2-3</div>
                    <h2 class="text-display section-title">Как записаться?</h2>
                    <p class="text-body section-subtitle">Три простых шага — и вы записаны к лучшему мастеру</p>
                </div>
                <div class="steps-grid">
                    <div class="card step-card">
                        <div class="step-number">1</div>
                        <span class="badge" style="margin-bottom: 0.5rem;">Шаг 01</span>
                        <h3 class="text-subtitle step-title">Найдите салон</h3>
                        <p class="step-desc">Выберите салон или услугу рядом с вами. Фильтры, рейтинги и отзывы помогут.</p>
                    </div>
                    <div class="card step-card">
                        <div class="step-number">2</div>
                        <span class="badge" style="margin-bottom: 0.5rem;">Шаг 02</span>
                        <h3 class="text-subtitle step-title">Выберите время</h3>
                        <p class="step-desc">Посмотрите свободные окна у мастера и выберите удобное время.</p>
                    </div>
                    <div class="card step-card">
                        <div class="step-number">3</div>
                        <span class="badge" style="margin-bottom: 0.5rem;">Шаг 03</span>
                        <h3 class="text-subtitle step-title">Готово!</h3>
                        <p class="step-desc">Приходите в назначенное время. Напоминание придёт заранее.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Популярные салоны -->
        <section class="section-py bg-surface-alt">
            <div class="section-container">
                <div class="section-header">
                    <h2 class="text-display section-title">Популярные салоны</h2>
                    <p class="text-muted section-subtitle">Лучшие салоны красоты по отзывам пользователей руми</p>
                </div>
                <div class="salon-cards-grid">
                    {salon_cards}
                </div>
                <div style="text-align: center; margin-top: 2.5rem;">
                    <a href="/salons" class="btn-outline">Смотреть все салоны →</a>
                </div>
            </div>
        </section>

        {render_footer()}
    </main>
</body>
</html>"""
    
    return html