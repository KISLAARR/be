# app/web/pages/settings.py
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles


def render_settings_page(user=None) -> str:
    """Страница настроек."""
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Настройки — руми</title>
    {get_base_styles()}
</head>
<body>
    {render_header("settings")}
    {render_sidebar("settings", user)}
    
    <main style="margin-right: 16rem; padding-top: 2rem;">
        <div class="section-container">
            <h1 class="text-display" style="font-size:2rem;margin-bottom:2rem">Настройки</h1>
            
            <div class="card" style="margin-bottom:1.5rem">
                <h2 class="text-subtitle" style="font-size:1.1rem;margin-bottom:1rem">Профиль</h2>
                <div style="margin-bottom:1rem">
                    <label style="display:block;font-weight:500;margin-bottom:0.5rem">Имя</label>
                    <input type="text" placeholder="Ваше имя" style="width:100%;padding:0.75rem;border:1px solid var(--color-border);border-radius:0.5rem">
                </div>
                <div style="margin-bottom:1rem">
                    <label style="display:block;font-weight:500;margin-bottom:0.5rem">Телефон</label>
                    <input type="tel" placeholder="+7XXXXXXXXXX" style="width:100%;padding:0.75rem;border:1px solid var(--color-border);border-radius:0.5rem">
                </div>
                <button class="btn-primary">Сохранить</button>
            </div>
            
            <div class="card" style="margin-bottom:1.5rem">
                <h2 class="text-subtitle" style="font-size:1.1rem;margin-bottom:1rem">Уведомления</h2>
                <div style="margin-bottom:0.75rem">
                    <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer">
                        <input type="checkbox" checked> Напоминания о записях
                    </label>
                </div>
                <div style="margin-bottom:0.75rem">
                    <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer">
                        <input type="checkbox" checked> Новые акции салонов
                    </label>
                </div>
            </div>
            
            <div class="card" style="border-color:red">
                <h2 class="text-subtitle" style="font-size:1.1rem;margin-bottom:0.5rem;color:red">Опасная зона</h2>
                <p class="text-muted" style="font-size:0.85rem;margin-bottom:1rem">После удаления аккаунта восстановить его невозможно.</p>
                <button class="btn-outline" style="color:red;border-color:red">Удалить аккаунт</button>
            </div>
        </div>
    </main>
    
    {render_footer()}
</body>
</html>"""
    
    return html