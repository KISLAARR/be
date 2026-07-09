# app/web/pages/model_landing.py
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles
from app.web.components.icons import (
    ICON_CAMERA,
    ICON_SPARKLES,
    ICON_USER_PLUS,
    ICON_SEARCH,
    ICON_CALENDAR_CHECK,
    ICON_CIRCLE_CHECK,
    ICON_ARROW_RIGHT,
)

# Если какой-то иконки нет в icons.py, добавим её, но в проекте уже есть многие.
# Я проверю: ICON_CAMERA, ICON_USER_PLUS, ICON_CALENDAR_CHECK есть? В icons.py, который вы скинули, есть ICON_SEARCH, ICON_SPARKLES, ICON_ARROW_RIGHT, ICON_CIRCLE_CHECK.
# Добавим недостающие в icons.py или используем существующие подходящие.

def render_model_landing_page(user=None) -> str:
    """Страница «Стань моделью» (лендинг)."""
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Стань моделью | Руми</title>
    <meta name="description" content="Оформи подписку и получай услуги от лучших мастеров по специальным ценам.">
    {get_base_styles()}
    <link rel="stylesheet" href="/static/src/css/model-landing.css">
</head>
<body>
    {render_header("model")}
    {render_sidebar("model", user)}

    <main class="home-main">
        <!-- Hero -->
        <section class="model-hero">
            <div class="section-container">
                <div class="model-hero-content">
                    <div class="model-hero-badge">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-camera h-4 w-4" aria-hidden="true"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path><circle cx="12" cy="13" r="3"></circle></svg>
                        <span>Подписка «Модель»</span>
                    </div>
                    <h1 class="model-hero-title">Стань моделью в <span class="highlight">руми</span></h1>
                    <p class="model-hero-subtitle">Получай услуги от лучших мастеров по сниженным ценам. Пробуй новые процедуры, помогай мастерам совершенствовать навыки и создавай образ мечты.</p>
                    <div class="model-hero-buttons">
                        <a href="#plans" class="model-hero-btn-primary">
                            Смотреть тарифы
                            {ICON_ARROW_RIGHT}
                        </a>
                        <a href="#how-it-works" class="model-hero-btn-secondary">Как это работает?</a>
                    </div>
                </div>
            </div>
        </section>

        <!-- Тарифы -->
        <section id="plans" class="section-py model-plans">
            <div class="section-container">
                <div class="section-header-center">
                    <span class="badge">Тарифы</span>
                    <h2>Выбери свой план</h2>
                    <p>Три тарифа на любой бюджет — от пробного до безлимитного</p>
                </div>
                <div class="plans-grid">
                    <!-- Старт -->
                    <div class="plan-card">
                        <div class="plan-header">
                            <h3 class="plan-name">Старт</h3>
                            <p class="plan-desc">Для тех, кто хочет попробовать</p>
                        </div>
                        <div class="plan-price">
                            <span class="amount">490 ₽</span>
                            <span class="period">/мес</span>
                        </div>
                        <ul class="plan-features">
                            <li>{ICON_CIRCLE_CHECK}<span>До 3 записей в месяц</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Скидка 30% на услуги мастеров</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Доступ к начинающим мастерам</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Базовое портфолио</span></li>
                        </ul>
                        <a href="/model/checkout?plan=start" class="plan-btn">
                            Оформить подписку
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>

                    <!-- Про (популярный) -->
                    <div class="plan-card popular">
                        <div class="popular-badge">Популярный</div>
                        <div class="plan-header">
                            <h3 class="plan-name">Про</h3>
                            <p class="plan-desc">Самый популярный выбор</p>
                        </div>
                        <div class="plan-price">
                            <span class="amount">990 ₽</span>
                            <span class="period">/мес</span>
                        </div>
                        <ul class="plan-features">
                            <li>{ICON_CIRCLE_CHECK}<span>До 8 записей в месяц</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Скидка 50% на все услуги</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Приоритетная запись</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Доступ к топ-мастерам</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Расширенное портфолио</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Эксклюзивные процедуры</span></li>
                        </ul>
                        <a href="/model/checkout?plan=pro" class="plan-btn">
                            Оформить подписку
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>

                    <!-- Премиум -->
                    <div class="plan-card">
                        <div class="plan-header">
                            <h3 class="plan-name">Премиум</h3>
                            <p class="plan-desc">Максимум возможностей</p>
                        </div>
                        <div class="plan-price">
                            <span class="amount">1 990 ₽</span>
                            <span class="period">/мес</span>
                        </div>
                        <ul class="plan-features">
                            <li>{ICON_CIRCLE_CHECK}<span>Безлимитные записи</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Скидка до 70% на услуги</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>VIP приоритет на запись</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Доступ ко всем мастерам</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Персональный менеджер</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Фотосессии для портфолио</span></li>
                            <li>{ICON_CIRCLE_CHECK}<span>Ранний доступ к новым салонам</span></li>
                        </ul>
                        <a href="/model/checkout?plan=premium" class="plan-btn">
                            Оформить подписку
                            {ICON_ARROW_RIGHT}
                        </a>
                    </div>
                </div>
            </div>
        </section>

        <!-- Партнёр Альфа-Банк -->
        <section class="section-py model-partner">
            <div class="section-container">
                <div class="partner-horizontal">
                    <div class="partner-horizontal-inner">
                        <div class="partner-h-left">
                            <div class="partner-h-logo">
                                <span class="partner-h-letter">A</span>
                            </div>
                            <div>
                                <p class="partner-h-name">Альфа-Банк</p>
                                <span class="partner-h-label">Партнёр руми</span>
                            </div>
                        </div>
                        <p class="partner-h-text">
                            Оплачивай подписку Альфа‑Картой — <span style="color: #EE3424; font-weight: 600;">кешбэк 5%</span>
                        </p>
                        <a href="https://alfabank.ru" target="_blank" rel="noopener noreferrer" class="partner-h-btn">
                            Оформить карту
                        </a>
                    </div>
                    <div class="partner-h-footer">
                        <span>Реклама • Альфа-Банк • alfabank.ru</span>
                        <span>18+</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- Как это работает -->
        <section id="how-it-works" class="section-py model-how">
            <div class="section-container">
                <div class="section-header-center">
                    <span class="badge">Как это работает</span>
                    <h2>4 простых шага</h2>
                    <p>От регистрации до записи — всё просто и быстро</p>
                </div>
                <div class="how-steps-grid">
                    <div class="how-step-item">
                        <div class="step-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-user-plus h-7 w-7 text-white" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><line x1="19" x2="19" y1="8" y2="14"></line><line x1="22" x2="16" y1="11" y2="11"></line></svg>
                        </div>
                        <div class="step-number">1</div>
                        <h3>Зарегистрируйся</h3>
                        <p>Создай аккаунт в руми и заполни профиль — расскажи о себе, загрузи фото.</p>
                    </div>
                    <div class="how-step-item">
                        <div class="step-icon">
                            {ICON_SPARKLES}
                        </div>
                        <div class="step-number">2</div>
                        <h3>Выбери подписку</h3>
                        <p>Выбери тариф, который подходит именно тебе — от Старт до Премиум.</p>
                    </div>
                    <div class="how-step-item">
                        <div class="step-icon">
                            {ICON_SEARCH}
                        </div>
                        <div class="step-number">3</div>
                        <h3>Найди мастера</h3>
                        <p>Ищи мастеров по рейтингу, отзывам и услугам. Фильтруй по расстоянию.</p>
                    </div>
                    <div class="how-step-item">
                        <div class="step-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-calendar-check h-7 w-7 text-white" aria-hidden="true"><path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path><path d="m9 16 2 2 4-4"></path></svg>
                        </div>
                        <div class="step-number">4</div>
                        <h3>Запишись на приём</h3>
                        <p>Выбери удобное время и получи услугу со скидкой. Мастер уже ждёт!</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- FAQ -->
        <section class="section-py model-faq">
            <div class="section-container">
                <div class="section-header-center">
                    <span class="badge">Вопросы</span>
                    <h2>Частые вопросы</h2>
                </div>
                <div class="faq-list">
                    <div class="faq-item">
                        <button class="faq-question">Что значит «стать моделью»? <span class="faq-icon">+</span></button>
                        <div class="faq-answer" style="display:none;">Стать моделью — значит получить доступ к специальным ценам на услуги мастеров, помогая им совершенствовать навыки. Вы получаете скидки, приоритетную запись и эксклюзивные предложения.</div>
                    </div>
                    <div class="faq-item">
                        <button class="faq-question">Кто может стать моделью? <span class="faq-icon">+</span></button>
                        <div class="faq-answer" style="display:none;">Любой желающий, достигший 18 лет. Вам не нужен опыт моделирования — вы просто записываетесь на услуги по сниженной цене.</div>
                    </div>
                    <div class="faq-item">
                        <button class="faq-question">Могу ли я отменить подписку? <span class="faq-icon">+</span></button>
                        <div class="faq-answer" style="display:none;">Да, вы можете отменить подписку в любой момент в настройках профиля. Следующий месяц списан не будет.</div>
                    </div>
                    <div class="faq-item">
                        <button class="faq-question">Какие услуги доступны по подписке? <span class="faq-icon">+</span></button>
                        <div class="faq-answer" style="display:none;">Все услуги, представленные на платформе: стрижки, окрашивание, маникюр, педикюр, массаж и многое другое. Конкретный список зависит от мастеров.</div>
                    </div>
                    <div class="faq-item">
                        <button class="faq-question">Как мастера выбирают моделей? <span class="faq-icon">+</span></button>
                        <div class="faq-answer" style="display:none;">Мастера сами публикуют запросы на модели для отработки новых техник или для портфолио. Вы можете откликаться на подходящие предложения.</div>
                    </div>
                    <div class="faq-item">
                        <button class="faq-question">Что входит в портфолио? <span class="faq-icon">+</span></button>
                        <div class="faq-answer" style="display:none;">В портфолио входят профессиональные фото ваших образов, созданные мастерами. Это помогает вам получать ещё больше предложений.</div>
                    </div>
                </div>
            </div>
        </section>

        {render_footer()}
    </main>

    <script>
        // Простой аккордеон для FAQ
        document.querySelectorAll('.faq-question').forEach(button => {{
            button.addEventListener('click', function() {{
                const answer = this.nextElementSibling;
                const icon = this.querySelector('.faq-icon');
                if (answer.style.display === 'none' || !answer.style.display) {{
                    answer.style.display = 'block';
                    icon.textContent = '−';
                }} else {{
                    answer.style.display = 'none';
                    icon.textContent = '+';
                }}
            }});
        }});
    </script>
</body>
</html>"""
    return html