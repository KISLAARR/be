# app/web/pages/model_checkout.py
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.styles import get_base_styles


def render_model_checkout(plan: str) -> str:
    """Страница оформления подписки."""
    
    plans = {
        "start": {"name": "Старт", "price": "490", "discount": "30%"},
        "pro": {"name": "Про", "price": "990", "discount": "50%"},
        "premium": {"name": "Премиум", "price": "1 990", "discount": "70%"},
    }
    
    plan_info = plans.get(plan, plans["start"])
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Оформление подписки — {plan_info['name']} — руми</title>
    {get_base_styles()}
</head>
<body style="display:flex;align-items:center;justify-content:center;min-height:100vh;background:var(--color-surface-alt)">
<div class="card" style="width:100%;max-width:480px;padding:2.5rem">
    <div style="text-align:center;margin-bottom:1.5rem;font-size:1.5rem;font-weight:800"><span style="color:var(--color-primary)">руми.</span></div>
    <h1 style="font-size:1.5rem;color:var(--color-heading);text-align:center;margin-bottom:0.5rem">Оформление подписки</h1>
    <p style="text-align:center;color:var(--color-muted);margin-bottom:1.5rem">Тариф <strong>{plan_info['name']}</strong> · {plan_info['price']} ₽/мес · Скидка {plan_info['discount']}</p>
    
    <form>
        <label style="display:block;font-weight:500;margin-bottom:0.5rem">Номер карты</label>
        <input type="text" placeholder="0000 0000 0000 0000" style="width:100%;padding:0.75rem;border:1px solid var(--color-border);border-radius:0.5rem;margin-bottom:1rem;font-size:1rem">
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem">
            <div>
                <label style="display:block;font-weight:500;margin-bottom:0.5rem">Срок</label>
                <input type="text" placeholder="ММ/ГГ" style="width:100%;padding:0.75rem;border:1px solid var(--color-border);border-radius:0.5rem">
            </div>
            <div>
                <label style="display:block;font-weight:500;margin-bottom:0.5rem">CVC</label>
                <input type="text" placeholder="123" style="width:100%;padding:0.75rem;border:1px solid var(--color-border);border-radius:0.5rem">
            </div>
        </div>
        
        <button type="submit" class="btn-primary" style="width:100%;padding:1rem;font-size:1rem">Оплатить {plan_info['price']} ₽</button>
    </form>
    
    <div style="margin-top:1rem;padding:0.75rem;background:#fef3f0;border-radius:0.5rem;text-align:center;font-size:0.8rem;color:var(--color-muted)">
        🔒 Платёж защищён · <span style="color:#EE3424">Альфа-Банк</span>
    </div>
    
    <p style="text-align:center;margin-top:1rem;font-size:0.8rem"><a href="/model">← Выбрать другой тариф</a></p>
</div>
</body>
</html>"""
    
    return html