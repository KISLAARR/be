# app/web/components/sidebar.py
from app.web.components.icons import (
    ICON_HOUSE,
    ICON_BUILDING2,
    ICON_BRIEFCASE,
    ICON_GIFT,
    ICON_FILE_TEXT,
    ICON_USER,
    ICON_MODEL,
)

def render_sidebar(current_page: str = "home", user=None) -> str:
    def is_active(page: str) -> str:
        return "active" if current_page == page else ""

    # Блок имени и фото пользователя
    if user:
        name = user.full_name or user.phone or "Пользователь"
        if user.avatar_url:
            avatar_html = f'<img src="{user.avatar_url}" alt="{name}" class="sidebar-avatar-img">'
        else:
            avatar_html = f'<span class="sidebar-avatar-placeholder">{name[0].upper()}</span>'
        
        user_block = f"""
        <div class="sidebar-user">
            <div class="sidebar-avatar">
                {avatar_html}
            </div>
            <span class="sidebar-username">{name}</span>
        </div>
        """
    else:
        user_block = f"""
        <a class="sidebar-link" href="/login" style="font-weight: 600; color: var(--color-primary);">
            {ICON_USER} Войти
        </a>
        """

    # Ролевые разделы (потерялись при редизайне): админка и панель бизнеса
    role_items = ""
    role = getattr(getattr(user, "role", None), "value", None)
    if role == "admin":
        role_items += f"""
                    <a class="sidebar-link {is_active('admin')}" href="/admin">
                        {ICON_USER} Админ-панель
                    </a>"""
    if role == "business":
        role_items += f"""
                    <a class="sidebar-link {is_active('business_dashboard')}" href="/business/dashboard">
                        {ICON_BRIEFCASE} Панель бизнеса
                    </a>"""
    role_links = ""
    if role_items:
        role_links = f"""
                <div class="space-y-1" style="margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid var(--color-border,#E5E7EB)">
                    {role_items}
                </div>"""

    return f"""
    <!-- Оверлей для затемнения -->
    <div class="sidebar-overlay" id="sidebar-overlay"></div>

    <!-- Сайдбар -->
    <aside class="sidebar-container" id="sidebar">
        <div class="sidebar-inner">
            <div class="sidebar-header" style="justify-content: flex-start; border-bottom: none; padding-bottom: 0.5rem;">
                {user_block}
            </div>

            <nav class="sidebar-nav">
                <div class="space-y-1">
                    <a class="sidebar-link {is_active('home')}" href="/">
                        {ICON_HOUSE} Главная
                    </a>
                    <a class="sidebar-link {is_active('salons')}" href="/salons">
                        {ICON_BUILDING2} Салоны
                    </a>
                    <a class="sidebar-link {is_active('business')}" href="/business">
                        {ICON_BRIEFCASE} Для бизнеса
                    </a>
                    <a class="sidebar-link {is_active('model')}" href="/model">
                        {ICON_MODEL} Стать моделью
                    </a>
                    <a class="sidebar-link {is_active('offer')}" href="/offer">
                        {ICON_GIFT} Предложение
                    </a>
                    <a class="sidebar-link {is_active('manifest')}" href="/about">
                        {ICON_FILE_TEXT} Манифест
                    </a>
                </div>{role_links}
            </nav>
        </div>
    </aside>
    """