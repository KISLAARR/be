# app/web/components/header.py

def render_header(current_page: str = "home", user=None) -> str:
    """Возвращает HTML-шапку сайта."""
    
    nav_links = [
        ("/", "Главная", "home"),
        ("/salons", "Салоны", "salons"),
    ]
    
    links_html = ""
    for url, title, page_id in nav_links:
        active = "font-weight: 700; color: var(--color-primary);" if current_page == page_id else ""
        links_html += f'<a href="{url}" style="margin-left: 2rem; text-decoration: none; color: var(--color-body); font-weight: 500; {active}">{title}</a>'
    
    # Блок авторизации
    if user:
        auth_block = f"""
        <a href="/profile" style="margin-left: 1.5rem; text-decoration: none; color: var(--color-heading); font-weight: 600;">
            👤 {user.full_name or 'Профиль'}
        </a>
        <a href="/logout" style="margin-left: 1rem; color: var(--color-muted); text-decoration: none; font-size: 0.85rem;">Выйти</a>
        """
    else:
        auth_block = '<a href="/login" class="btn-primary" style="margin-left: 2rem;">Войти</a>'
    
    return f"""
    <header style="background: white; border-bottom: 1px solid var(--color-border); padding: 1rem 2rem; position: sticky; top: 0; z-index: 100;">
        <nav style="display: flex; justify-content: space-between; align-items: center; max-width: 1280px; margin: 0 auto;">
            <a href="/" style="font-family: var(--font-heading); font-size: 1.5rem; font-weight: 800; color: var(--color-primary); text-decoration: none;">руми.</a>
            <div style="display: flex; align-items: center;">
                {links_html}
                {auth_block}
            </div>
        </nav>
    </header>
    """