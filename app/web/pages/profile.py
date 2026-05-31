# app/web/pages/profile.py
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles


def render_profile_page(user=None) -> str:
    """Страница профиля клиента."""
    
    if user:
        name = user.full_name or "Пользователь"
        role_text = {
            "client": "Клиент",
            "business": "Владелец салона",
            "model": "Модель",
            "master": "Мастер",
            "admin": "Администратор",
        }.get(user.role.value if user.role else "client", "Клиент")
        phone = user.phone or "—"
        avatar_letter = name[0].upper() if name else "?"
        login_block = ""
        stats = f"""
        <div class="stat-card">
            <div class="stat-value">0</div>
            <div class="stat-label">Записей</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">0</div>
            <div class="stat-label">Отзывов</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">0</div>
            <div class="stat-label">Избранных</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">0</div>
            <div class="stat-label">Бонусов</div>
        </div>
        """
        edit_form = f"""
        <div class="card" style="margin-top:1.5rem">
            <h3 style="margin-bottom:1rem">Редактировать профиль</h3>
            <form action="/api/v1/users/me" method="post">
                <div style="margin-bottom:1rem">
                    <label style="display:block;font-weight:500;margin-bottom:0.5rem">Имя</label>
                    <input type="text" name="full_name" value="{name}" style="width:100%;padding:0.75rem;border:1px solid var(--color-border);border-radius:0.5rem;font-size:0.9rem">
                </div>
                <div style="margin-bottom:1rem">
                    <label style="display:block;font-weight:500;margin-bottom:0.5rem">Телефон</label>
                    <input type="tel" name="phone" value="{phone}" style="width:100%;padding:0.75rem;border:1px solid var(--color-border);border-radius:0.5rem;font-size:0.9rem">
                </div>
                <button type="submit" class="btn-primary">💾 Сохранить</button>
            </form>
        </div>
        """
    else:
        name = "Гость"
        role_text = "Не авторизован"
        phone = "—"
        avatar_letter = "?"
        login_block = '<a href="/login" class="btn-primary" style="display:inline-block;margin-top:1rem">Войти в аккаунт</a>'
        stats = ""
        edit_form = ""
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Мой профиль — руми</title>
    {get_base_styles()}
    <style>
        .profile-header {{
            display: flex;
            gap: 2rem;
            align-items: center;
            margin-bottom: 2rem;
        }}
        .avatar {{
            width: 6rem;
            height: 6rem;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            color: white;
            font-weight: 700;
            flex-shrink: 0;
        }}
        .profile-info h1 {{
            font-size: 1.75rem;
            margin-bottom: 0.25rem;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        @media (max-width: 768px) {{
            .stat-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        .stat-card {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 1rem;
            padding: 1.25rem;
            text-align: center;
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--color-primary);
        }}
        .stat-label {{
            font-size: 0.8rem;
            color: var(--color-muted);
            margin-top: 0.25rem;
        }}
    </style>
</head>
<body>
    {render_header("profile", user)}
    {render_sidebar("profile")}
    
    <main style="margin-right: 16rem; padding-top: 2rem;">
        <div class="section-container">
            <div class="card" style="margin-bottom:2rem">
                <div class="profile-header">
                    <div class="avatar">{avatar_letter}</div>
                    <div class="profile-info">
                        <h1 class="text-display">{name}</h1>
                        <p class="text-muted">{role_text}</p>
                        <p class="text-muted" style="font-size:0.85rem">📱 {phone}</p>
                        {login_block}
                    </div>
                </div>
            </div>
            
            <div class="stat-grid">
                {stats}
            </div>
            
            <div class="card" style="margin-bottom:1.5rem">
                <h3 style="margin-bottom:1rem">Предстоящие записи</h3>
                <p class="text-muted">У вас пока нет записей. <a href="/salons">Найдите салон</a> и запишитесь!</p>
            </div>
            
            {edit_form}
        </div>
    </main>
    
    {render_footer()}
</body>
</html>"""
    
    return html