# app/web/pages/favorites.py
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles


def render_favorites_page() -> str:
    """Страница 'Избранное' для клиента."""
    
    # Показываем заглушку — функционал избранного можно добавить позже
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Избранное — руми</title>
    {get_base_styles()}
    <style>
        .empty-state {{
            text-align: center;
            padding: 4rem 2rem;
            max-width: 500px;
            margin: 0 auto;
        }}
        .empty-icon {{
            font-size: 4rem;
            margin-bottom: 1.5rem;
        }}
        .empty-state h2 {{
            font-size: 1.5rem;
            color: var(--color-heading);
            margin-bottom: 0.75rem;
        }}
        .empty-state p {{
            color: var(--color-muted);
            margin-bottom: 2rem;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    {render_header("favorites", None)}
    {render_sidebar("favorites")}
    
    <main style="margin-right: 16rem; padding-top: 2rem;">
        <div class="section-container">
            <h1 class="text-display" style="font-size:2rem;margin-bottom:2rem">Избранное</h1>
            
            <div class="empty-state">
                <div class="empty-icon">❤️</div>
                <h2>Пока пусто</h2>
                <p>Добавляйте салоны в избранное, нажимая на сердечко в карточке салона. Здесь будут храниться все понравившиеся вам места.</p>
                <a href="/salons" class="btn-primary">Найти салоны</a>
            </div>
        </div>
    </main>
    
    {render_footer()}
</body>
</html>"""
    
    return html