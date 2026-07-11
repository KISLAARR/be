# app/web/pages/offer_landing.py
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
    ICON_CIRCLE_CHECK,
    ICON_ARROW_RIGHT,
    ICON_ZAP,
    ICON_CIRCLE_X,
    ICON_CREDIT_CARD,
    ICON_PERCENT,
    ICON_STORE,
    ICON_SPARKLES,
)


def render_offer_landing_page(user=None) -> str:
    """Страница «Коммерческое предложение» (лендинг)."""

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Коммерческое предложение | Руми</title>
    <meta name="description" content="руми — платформа для салонов красоты: онлайн-запись, оплаты и касса через Т‑Банк, управление командой, аналитика и поток клиентов из маркетплейса.">
    {get_base_styles()}
    <link rel="stylesheet" href="/static/src/css/offer-landing.css">
</head>
<body>
    {render_header("offer")}
    {render_sidebar("offer", user)}

    <main class="home-main">

        <!-- HERO (тёмный) -->
        <section class="offer-hero">
            <div class="section-container">
                <div class="offer-hero-content">
                    <span class="offer-hero-badge">Коммерческое предложение</span>
                    <h1 class="offer-hero-title">руми — платформа, которая приводит клиентов и управляет салоном</h1>
                    <p class="offer-hero-subtitle">Запись, оплаты, касса, команда и аналитика — в одном окне. Плюс поток новых клиентов из маркетплейса. Эквайринг — Т‑Банк, из коробки.</p>
                    <div class="offer-hero-buttons">
                        <a href="/business/checkout?plan=business" class="offer-hero-btn-primary">
                            Подключить салон
                            {ICON_ARROW_RIGHT}
                        </a>
                        <a href="#pricing" class="offer-hero-btn-secondary">Смотреть тарифы</a>
                    </div>
                </div>

                <!-- Статистика -->
                <div class="offer-stats">
                    <div class="offer-stat-item">
                        <p class="offer-stat-value">−50%</p>
                        <p class="offer-stat-label">неявок клиентов</p>
                    </div>
                    <div class="offer-stat-item">
                        <p class="offer-stat-value">4 клика</p>
                        <p class="offer-stat-label">до записи</p>
                    </div>
                    <div class="offer-stat-item">
                        <p class="offer-stat-value">0 ₽</p>
                        <p class="offer-stat-label">подключение кассы</p>
                    </div>
                    <div class="offer-stat-item">
                        <p class="offer-stat-value">5%</p>
                        <p class="offer-stat-label">кешбэк клиентам</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Закрываем реальные боли -->
        <section class="section-py offer-pains">
            <div class="section-container">
                <div class="section-header-center">
                    <span class="badge">Зачем это салону</span>
                    <h2>Закрываем реальные боли</h2>
                </div>
                <div class="pains-grid">
                    <!-- Карточка 1 -->
                    <div class="pain-card">
                        <div class="pain-header">
                            {ICON_CIRCLE_X}
                            <span class="pain-title">Долгий поиск клиентов для новых мастеров</span>
                        </div>
                        <div class="pain-solution">
                            {ICON_CIRCLE_CHECK}
                            <p>Программа «Модели» заполняет слоты клиентами. Мастера набирают практику и портфолио, а салон получает оборот вместо простоя.</p>
                        </div>
                        <a href="#pricing" class="pain-link">
                            {ICON_TRENDING_UP}
                            <span>Загрузка новых мастеров без затрат на рекламу</span>
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>

                    <!-- Карточка 2 -->
                    <div class="pain-card">
                        <div class="pain-header">
                            {ICON_CIRCLE_X}
                            <span class="pain-title">Записи срываются, клиенты не приходят</span>
                        </div>
                        <div class="pain-solution">
                            {ICON_CIRCLE_CHECK}
                            <p>Онлайн-предоплата через Т‑Банк закрепляет бронь. Клиент, который оплатил вперёд, почти всегда доходит, а свободные слоты не простаивают впустую.</p>
                        </div>
                        <a href="#pricing" class="pain-link">
                            {ICON_TRENDING_UP}
                            <span>Снижение неявок (no-show) до 50%</span>
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>

                    <!-- Карточка 3 -->
                    <div class="pain-card">
                        <div class="pain-header">
                            {ICON_CIRCLE_X}
                            <span class="pain-title">Новых клиентов мало, реклама дорогая</span>
                        </div>
                        <div class="pain-solution">
                            {ICON_CIRCLE_CHECK}
                            <p>Салон попадает в маркетплейс руми — витрину, куда люди приходят искать, где постричься. Это поток новых клиентов, а не просто хранилище для текущих.</p>
                        </div>
                        <a href="#pricing" class="pain-link">
                            {ICON_TRENDING_UP}
                            <span>Новые клиенты из поиска без бюджета на привлечение</span>
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>

                    <!-- Карточка 4 -->
                    <div class="pain-card">
                        <div class="pain-header">
                            {ICON_CIRCLE_X}
                            <span class="pain-title">Клиенты не могут дозвониться, чтобы записаться</span>
                        </div>
                        <div class="pain-solution">
                            {ICON_CIRCLE_CHECK}
                            <p>Онлайн-запись за 4 клика — без звонков и форм. Клиент выбирает услугу, мастера и время сам, в любое время суток, а расписание обновляется в реальном времени.</p>
                        </div>
                        <a href="#pricing" class="pain-link">
                            {ICON_TRENDING_UP}
                            <span>До 40% записей приходят вне рабочих часов администратора</span>
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>

                    <!-- Карточка 5 -->
                    <div class="pain-card">
                        <div class="pain-header">
                            {ICON_CIRCLE_X}
                            <span class="pain-title">Касса, чеки и 54-ФЗ — отдельная головная боль</span>
                        </div>
                        <div class="pain-solution">
                            {ICON_CIRCLE_CHECK}
                            <p>Эквайринг, торговый терминал и онлайн-касса Т‑Банка подключаются из коробки. Фискальные чеки формируются автоматически — без отдельных договоров и интеграторов.</p>
                        </div>
                        <a href="#pricing" class="pain-link">
                            {ICON_TRENDING_UP}
                            <span>Подключение за 1 день, 0 ₽ за старт</span>
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>

                    <!-- Карточка 6 -->
                    <div class="pain-card">
                        <div class="pain-header">
                            {ICON_CIRCLE_X}
                            <span class="pain-title">Не видно, что реально приносит деньги</span>
                        </div>
                        <div class="pain-solution">
                            {ICON_CIRCLE_CHECK}
                            <p>Понятные дашборды: выручка, загрузка по мастерам, средний чек, возвраты клиентов. Видно, какие услуги и сотрудники работают, а какие тянут вниз.</p>
                        </div>
                        <a href="#pricing" class="pain-link">
                            {ICON_TRENDING_UP}
                            <span>Решения по цифрам, а не по ощущениям</span>
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>
                </div>
            </div>
        </section>

        <!-- Возможности (Всё для салона) -->
        <section class="section-py offer-features bg-surface-alt">
            <div class="section-container">
                <div class="section-header-center">
                    <span class="badge">Возможности</span>
                    <h2>Всё для салона в одном окне</h2>
                </div>
                <div class="offer-features-grid">
                    <div class="offer-feature-card">
                        <div class="offer-feature-icon">{ICON_CALENDAR_DAYS}</div>
                        <h3>Онлайн-запись</h3>
                        <p>Клиент выбирает услугу, салон и время за 4 клика. Расписание обновляется в реальном времени.</p>
                    </div>
                    <div class="offer-feature-card">
                        <div class="offer-feature-icon">{ICON_CREDIT_CARD}</div>
                        <h3>Оплаты и касса</h3>
                        <p>Онлайн-предоплата и торговый терминал через Т‑Банк. Фискальные чеки и 54-ФЗ закрыты.</p>
                    </div>
                    <div class="offer-feature-card">
                        <div class="offer-feature-icon">{ICON_USERS}</div>
                        <h3>Управление командой</h3>
                        <p>Расписание мастеров, зарплаты, доступы и нагрузка — в одном окне.</p>
                    </div>
                    <div class="offer-feature-card">
                        <div class="offer-feature-icon">{ICON_CHART_COLUMN}</div>
                        <h3>Аналитика</h3>
                        <p>Выручка, загрузка, средний чек, возвраты клиентов — понятные дашборды.</p>
                    </div>
                    <div class="offer-feature-card">
                        <div class="offer-feature-icon">{ICON_SPARKLES}</div>
                        <h3>Программа «Модели»</h3>
                        <p>Заполняйте пустые окна моделями со скидкой — мастера набирают практику, вы получаете оборот.</p>
                    </div>
                    <div class="offer-feature-card">
                        <div class="offer-feature-icon">{ICON_TRENDING_UP}</div>
                        <h3>Продвижение</h3>
                        <p>Приоритет в выдаче, акции и программы лояльности привлекают новых клиентов.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Партнёр Т‑Банк (жёлтый) -->
        <section class="section-py offer-partner">
            <div class="section-container">
                <div class="offer-partner-block">
                    <div class="offer-partner-inner">
                        <div class="offer-partner-left">
                            <div class="offer-partner-logo">
                                <span class="offer-partner-letter">Т</span>
                                <div>
                                    <p class="offer-partner-name">Т‑Банк</p>
                                    <p class="offer-partner-label">Официальный партнёр по эквайрингу</p>
                                </div>
                            </div>
                            <h2 class="offer-partner-title">Оплаты и касса — из коробки</h2>
                            <p class="offer-partner-desc">Онлайн-эквайринг для предоплаты записей, торговые терминалы в зале и онлайн-касса для 54-ФЗ. Один партнёр вместо трёх договоров — подключение за день, без платы за старт.</p>
                        </div>
                        <div class="offer-partner-right">
                            <div class="offer-partner-item">
                                <div class="offer-partner-item-icon">{ICON_CREDIT_CARD}</div>
                                <p class="offer-partner-item-value">Онлайн</p>
                                <p class="offer-partner-item-label">предоплата записей</p>
                            </div>
                            <div class="offer-partner-item">
                                <div class="offer-partner-item-icon">{ICON_STORE}</div>
                                <p class="offer-partner-item-value">Терминал</p>
                                <p class="offer-partner-item-label">оплата в зале</p>
                            </div>
                            <div class="offer-partner-item">
                                <div class="offer-partner-item-icon">{ICON_PERCENT}</div>
                                <p class="offer-partner-item-value">5%</p>
                                <p class="offer-partner-item-label">кешбэк клиентам</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Сравнение -->
        <section class="section-py offer-comparison bg-surface-alt">
            <div class="section-container">
                <div class="section-header-center">
                    <span class="badge">Сравнение</span>
                    <h2>Почему руми, а не другие</h2>
                </div>
                <div class="comparison-table">
                    <div class="comparison-header">
                        <span>Что важно салону</span>
                        <span class="comparison-brand">руми</span>
                        <span>Другие CRM</span>
                    </div>
                    <!-- Строки -->
                    <div class="comparison-row">
                        <span>Подключение эквайринга и кассы</span>
                        <span class="comparison-rumi">{ICON_CIRCLE_CHECK} Из коробки, 0 ₽</span>
                        <span class="comparison-other">Доплата + настройка</span>
                    </div>
                    <div class="comparison-row">
                        <span>Онлайн-предоплата за запись</span>
                        <span class="comparison-rumi">{ICON_CIRCLE_CHECK} Да, через Т‑Банк</span>
                        <span class="comparison-other">Через сторонние модули</span>
                    </div>
                    <div class="comparison-row">
                        <span>Маркетплейс клиентов</span>
                        <span class="comparison-rumi">{ICON_CIRCLE_CHECK} Встроен — поток новых клиентов</span>
                        <span class="comparison-other">Только CRM</span>
                    </div>
                    <div class="comparison-row">
                        <span>Программа «Модели»</span>
                        <span class="comparison-rumi">{ICON_CIRCLE_CHECK} Да — заполняет пустые окна</span>
                        <span class="comparison-other">Нет</span>
                    </div>
                    <div class="comparison-row">
                        <span>Стоимость входа</span>
                        <span class="comparison-rumi">{ICON_CIRCLE_CHECK} От 250 ₽ за сотрудника</span>
                        <span class="comparison-other">Выше, пакеты</span>
                    </div>
                    <div class="comparison-row">
                        <span>Кешбэк клиентам</span>
                        <span class="comparison-rumi">{ICON_CIRCLE_CHECK} 5% с Т‑Картой</span>
                        <span class="comparison-other">Нет</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- Тарифы -->
        <section id="pricing" class="section-py offer-pricing">
            <div class="section-container">
                <div class="section-header-center">
                    <span class="badge">Тарифы</span>
                    <h2>Простые и прозрачные цены</h2>
                    <p>Выберите тариф под размер салона. Эквайринг Т‑Банк включён во все тарифы.</p>
                </div>
                <div class="offer-pricing-grid">
                    <!-- Лайт -->
                    <div class="offer-pricing-card">
                        <h3 class="offer-plan-name">Лайт</h3>
                        <p class="offer-plan-sub">До 5 сотрудников</p>
                        <div class="offer-plan-price">
                            <span class="offer-price-amount">250 ₽</span>
                            <span class="offer-price-period">за сотрудника / мес</span>
                        </div>
                        <ul class="offer-plan-features">
                            <li>{ICON_CIRCLE_CHECK}<span>Оплата только за сотрудников</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Управление расписанием</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Онлайн-запись клиентов</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Эквайринг Т‑Банк</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Базовая аналитика</span></li>
                        </ul>
                        <a href="/business/checkout?plan=lite" class="offer-plan-btn">
                            Подключить
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>

                    <!-- Бизнес (популярный) -->
                    <div class="offer-pricing-card popular">
                        <div class="popular-badge">Популярный</div>
                        <h3 class="offer-plan-name">Бизнес</h3>
                        <p class="offer-plan-sub">От 5 до 10 сотрудников</p>
                        <div class="offer-plan-price">
                            <span class="offer-price-amount">3 500 ₽</span>
                            <span class="offer-price-period">/мес</span>
                        </div>
                        <ul class="offer-plan-features">
                            <li>{ICON_CIRCLE_CHECK}<span>Всё из тарифа «Лайт»</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Расширенная аналитика</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Приоритет в выдаче</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Онлайн-касса и торговый терминал</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Акции и программы лояльности</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Персональная поддержка</span></li>
                        </ul>
                        <a href="/business/checkout?plan=business" class="offer-plan-btn">
                            Подключить
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>

                    <!-- Корпоративный -->
                    <div class="offer-pricing-card">
                        <h3 class="offer-plan-name">Корпоративный</h3>
                        <p class="offer-plan-sub">От 10 до 20 сотрудников</p>
                        <div class="offer-plan-price">
                            <span class="offer-price-amount">6 990 ₽</span>
                            <span class="offer-price-period">/мес</span>
                        </div>
                        <ul class="offer-plan-features">
                            <li>{ICON_CIRCLE_CHECK}<span>Всё из тарифа «Бизнес»</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Мульти-филиалы</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>VIP поддержка</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Индивидуальные интеграции</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Расширенная отчётность</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Выделенный менеджер</span></li>
                        </ul>
                        <a href="/business/checkout?plan=corporate" class="offer-plan-btn">
                            Подключить
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>
                </div>
                <p class="offer-pricing-footer">Более 20 сотрудников? <a href="/business/checkout?plan=custom" class="text-link">Запросите индивидуальный тариф</a></p>
            </div>
        </section>

        {render_footer()}
    </main>
</body>
</html>"""
    return html