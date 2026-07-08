# app/web/pages/register.py
import html
from fastapi import Request
from app.web.components.styles import get_base_styles


def _alert(msg: str) -> str:
    if not msg:
        return ""
    return (
        '<div style="background:#FEE2E2;color:#991B1B;border:1px solid #FCA5A5;'
        'border-radius:0.5rem;padding:0.75rem 1rem;margin-bottom:1rem;font-size:0.875rem">'
        f'{msg}</div>'
    )


def render_register_page(request: Request) -> str:
    """Страница регистрации."""
    q = request.query_params
    phone = html.escape(q.get("phone", ""), quote=True)
    full_name = html.escape(q.get("full_name", ""), quote=True)
    errors = {
        "phone_exists": "Пользователь с таким телефоном уже зарегистрирован",
        "weak_password": "Пароль не отвечает требованиям сложности",
        "bad_phone": "Неверный формат телефона. Пример: +7 (999) 123-45-67",
    }
    banner = _alert(errors.get(q.get("error", ""), ""))

    scripts = """
    <script src="/static/js/phone-mask.js"></script>
    <script src="/static/js/password-validator.js"></script>
    """

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Регистрация — руми</title>
    {get_base_styles()}
    <link rel="stylesheet" href="/static/css/login-register.css">
</head>
<body class="auth-page">
    <div class="auth-card">
        <div class="auth-logo">руми.</div>
        <h1 class="auth-title">Регистрация</h1>
        {banner}
        <form action="/api/v1/auth/register-web" method="post">
            <div class="form-group">
                <label for="full_name">Имя</label>
                <input type="text" id="full_name" name="full_name" value="{full_name}" placeholder="Ваше имя">
            </div>
            <div class="form-group">
                <label for="phone">Телефон</label>
                <input type="tel" id="phone" name="phone" value="{phone}" placeholder="+7 (___) ___-__-__" class="phone-input" required>
            </div>
            <div class="form-group">
                <label for="password">Пароль</label>
                <input type="password" id="pw" name="password" required minlength="8">
                <ul class="password-rules">
                    <li data-rule="len"><span class="mark">✗</span> Минимум 8 символов</li>
                    <li data-rule="lower"><span class="mark">✗</span> Строчная буква</li>
                    <li data-rule="upper"><span class="mark">✗</span> Заглавная буква</li>
                    <li data-rule="digit"><span class="mark">✗</span> Цифра</li>
                </ul>
            </div>
            <button type="submit" id="submitBtn" class="btn-primary auth-btn" disabled>Зарегистрироваться</button>
        </form>
        <div class="auth-links">
            <a href="/login">Вход</a> · <a href="/">На главную</a>
        </div>
    </div>
    {scripts}
</body>
</html>"""