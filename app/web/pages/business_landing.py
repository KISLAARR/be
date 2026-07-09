# app/web/pages/business_landing.py
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles
from app.web.components.icons import (
    ICON_BRIEFCASE,
    ICON_CALENDAR_DAYS,
    ICON_CHART_COLUMN,
    ICON_USERS,
    ICON_SHIELD_CHECK,
    ICON_CLOCK,
    ICON_TRENDING_UP,
    ICON_BUILDING2,
    ICON_SETTINGS,
    ICON_MEGAPHONE,
    ICON_ROCKET,
    ICON_CIRCLE_CHECK,
    ICON_ARROW_RIGHT,
)


def render_business_landing_page(user=None) -> str:
    """Страница «Для бизнеса» (лендинг)."""

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Для бизнеса | Руми</title>
    <meta name="description" content="Управляйте своим салоном красоты легко — расписание, аналитика, клиенты.">
    {get_base_styles()}
    <link rel="stylesheet" href="/static/css/business.css">
</head>
<body>
    {render_header("business")}
    {render_sidebar("business", user)}

    <main class="home-main">
        <!-- Hero -->
        <section class="business-hero">
            <div class="section-container">
                <div class="business-hero-content">
                    <div class="business-hero-badge">
                        {ICON_BRIEFCASE}
                        <span>Для бизнеса</span>
                    </div>
                    <h1 class="business-hero-title">Управлять салоном — <span class="highlight">тоже просто<span class="highlight">.</span></span></h1>
                    <p class="business-hero-subtitle">Расписание, оплаты, клиенты, аналитика — всё в одном окне. Никаких таблиц, журналов и десяти разных программ.</p>
                    <div class="business-hero-buttons">
                        <a href="#pricing" class="business-hero-btn-primary">
                            Подключить салон
                            {ICON_ARROW_RIGHT}
                        </a>
                        <a href="#how-it-works" class="business-hero-btn-secondary">Как это работает?</a>
                    </div>
                </div>
            </div>
        </section>

        <!-- Возможности -->
        <section id="features" class="section-py business-features section-gradient-up>
            <div class="section-container">
                <div class="section-header-center">
                    <span class="badge">Возможности</span>
                    <h2>Всё для вашего салона</h2>
                    <p>От расписания до аналитики — управляйте бизнесом в одном месте</p>
                </div>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="icon-wrapper">{ICON_CALENDAR_DAYS}</div>
                        <h3>Управление расписанием</h3>
                        <p>Полный контроль над записями мастеров. Окна, отмены, переносы — всё в реальном времени. Клиенты записываются онлайн.</p>
                    </div>
                    <div class="feature-card">
                        <div class="icon-wrapper">{ICON_CHART_COLUMN}</div>
                        <h3>Аналитика доходов</h3>
                        <p>Отслеживайте выручку по дням, неделям и месяцам. Смотрите какие услуги приносят больше прибыли и кто из мастеров самый эффективный.</p>
                    </div>
                    <div class="feature-card">
                        <div class="icon-wrapper">{ICON_USERS}</div>
                        <h3>Привлечение клиентов</h3>
                        <p>Ваш салон видят тысячи пользователей руми. Рейтинг и отзывы помогают выделиться. Модели приходят сами.</p>
                    </div>
                    <div class="feature-card">
                        <div class="icon-wrapper">{ICON_SHIELD_CHECK}</div>
                        <h3>Проверенные клиенты</h3>
                        <p>Все пользователи верифицированы. Меньше отмен, больше лояльных клиентов, рейтинг доверия для каждого.</p>
                    </div>
                    <div class="feature-card">
                        <div class="icon-wrapper">{ICON_CLOCK}</div>
                        <h3>Экономия времени</h3>
                        <p>Автоматические напоминания клиентам, управление очередью, синхронизация с календарём — рутина на автопилоте.</p>
                    </div>
                    <div class="feature-card">
                        <div class="icon-wrapper">{ICON_TRENDING_UP}</div>
                        <h3>Рост бизнеса</h3>
                        <p>Инструменты для масштабирования: акции, программы лояльности, работа с несколькими филиалами из одного кабинета.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Как подключить -->
        <section id="how-it-works" class="section-py business-how section-gradient-down">
            <div class="section-container">
                <div class="section-header-center">
                    <span class="badge">Начало работы</span>
                    <h2>Как подключить салон</h2>
                    <p>4 шага — и ваш салон на платформе</p>
                </div>
                <div class="how-steps">
                    <div class="how-step">
                        <div class="step-icon">
                            <div class="icon-circle">{ICON_BUILDING2}</div>
                            <span class="step-number">Шаг 1</span>
                        </div>
                        <div class="step-content">
                            <h3>Зарегистрируйте салон</h3>
                            <p>Создайте профиль салона, добавьте фото, описание, адрес и список услуг.</p>
                        </div>
                    </div>
                    <div class="how-step">
                        <div class="step-icon">
                            <div class="icon-circle">{ICON_SETTINGS}</div>
                            <span class="step-number">Шаг 2</span>
                        </div>
                        <div class="step-content">
                            <h3>Настройте расписание</h3>
                            <p>Добавьте мастеров, их графики, услуги и цены. Всё настраивается за 15 минут.</p>
                        </div>
                    </div>
                    <div class="how-step">
                        <div class="step-icon">
                            <div class="icon-circle">{ICON_MEGAPHONE}</div>
                            <span class="step-number">Шаг 3</span>
                        </div>
                        <div class="step-content">
                            <h3>Привлекайте клиентов</h3>
                            <p>Ваш салон появится на платформе. Клиенты и модели начнут записываться.</p>
                        </div>
                    </div>
                    <div class="how-step">
                        <div class="step-icon">
                            <div class="icon-circle">{ICON_ROCKET}</div>
                            <span class="step-number">Шаг 4</span>
                        </div>
                        <div class="step-content">
                            <h3>Развивайте бизнес</h3>
                            <p>Используйте аналитику, акции и программы лояльности для роста.</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Тарифы -->
        <section id="pricing" class="section-py business-pricing">
            <div class="section-container">
                <div class="section-header-center">
                    <span class="badge">Тарифы</span>
                    <h2>Простые и прозрачные цены</h2>
                    <p>Выберите тариф под размер вашего салона. Более 20 сотрудников? Свяжитесь с нами для индивидуального предложения.</p>
                </div>
                <div class="pricing-grid">
                    <!-- Лайт -->
                    <div class="pricing-card">
                        <div class="plan-name">Лайт</div>
                        <div class="plan-sub">До 5 сотрудников</div>
                        <div class="plan-price">
                            <span class="amount">250 ₽</span>
                            <span class="period">за сотрудника/мес</span>
                        </div>
                        <ul class="plan-features">
                            <li>{ICON_CIRCLE_CHECK}<span>Оплата только за сотрудников</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Управление расписанием</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Онлайн-запись клиентов</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Базовая аналитика</span></li>
                        </ul>
                        <a href="/business/checkout?plan=lite" class="plan-btn">
                            Подключить
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>

                    <!-- Бизнес (популярный) -->
                    <div class="pricing-card popular">
                        <div class="popular-badge">Популярный</div>
                        <div class="plan-name">Бизнес</div>
                        <div class="plan-sub">От 5 до 10 сотрудников</div>
                        <div class="plan-price">
                            <span class="amount">3 500 ₽</span>
                            <span class="period">/мес</span>
                        </div>
                        <ul class="plan-features">
                            <li>{ICON_CIRCLE_CHECK}<span>Всё из тарифа «Лайт»</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Расширенная аналитика</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Приоритет в выдаче</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Акции и программы лояльности</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Персональная поддержка</span></li>
                        </ul>
                        <a href="/business/checkout?plan=business" class="plan-btn">
                            Подключить
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>

                    <!-- Корпоративный -->
                    <div class="pricing-card">
                        <div class="plan-name">Корпоративный</div>
                        <div class="plan-sub">От 10 до 20 сотрудников</div>
                        <div class="plan-price">
                            <span class="amount">6 990 ₽</span>
                            <span class="period">/мес</span>
                        </div>
                        <ul class="plan-features">
                            <li>{ICON_CIRCLE_CHECK}<span>Всё из тарифа «Бизнес»</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Мульти-филиалы</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>VIP поддержка</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Индивидуальные интеграции</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Расширенная отчётность</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Выделенный менеджер</span></li>
                        </ul>
                        <a href="/business/checkout?plan=corporate" class="plan-btn">
                            Подключить
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>
                </div>
                <div class="pricing-footer">
                    Более 20 сотрудников? <a href="/business/checkout/?plan=custom" class="text-link">Запросите индивидуальный тариф</a>
                </div>
            </div>
        </section>

        <!-- CTA -->
        <section class="section-py business-cta">
            <div class="section-container">
                <div class="cta-block">
                    <div class="bg-blob top-right"></div>
                    <div class="bg-blob bottom-left"></div>
                    <div class="cta-content">
                        <div class="cta-text">
                            <h2>Готовы начать?</h2>
                            <p>Подключите свой салон к руми и получите доступ к тысячам клиентов. Первые 14 дней — бесплатно.</p>
                            <a href="/business/checkout?plan=business" class="cta-btn">
                                Подключить салон
                                {ICON_ARROW_RIGHT}
                            </a>
                        </div>
                        <div class="cta-features">
                            <div class="cta-feature">
                                {ICON_CIRCLE_CHECK}
                                <span>Бесплатный пробный период — 14 дней</span>
                            </div>
                            <div class="cta-feature">
                                {ICON_CIRCLE_CHECK}
                                <span>Без скрытых комиссий и платежей</span>
                            </div>
                            <div class="cta-feature">
                                {ICON_CIRCLE_CHECK}
                                <span>Персональная поддержка при подключении</span>
                            </div>
                            <div class="cta-feature">
                                {ICON_CIRCLE_CHECK}
                                <span>Подключение за 15 минут</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        {render_footer()}
    </main>
</body>
</html>"""
    return html