# app/web/pages/salons.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Salon, Promotion
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles


async def render_salons_page(db: AsyncSession, user=None) -> str:
    """Страница со списком салонов в дизайне салоны.txt."""
    
    try:
        result = await db.execute(
            select(Salon).where(Salon.is_active == True).order_by(Salon.rating.desc())
        )
        salons = result.scalars().all()
    except Exception as e:
        salons = []
    
    # Карточки салонов
    salon_cards = ""
    for s in salons:
        # Получаем акции салона
        promos_result = await db.execute(
            select(Promotion).where(Promotion.salon_id == s.id, Promotion.is_active == True)
        )
        promotions = promos_result.scalars().all()
        
        # HTML для акций в боковой панели (десктоп)
        promos_desktop = ""
        for p in promotions:
            promos_desktop += f"""
            <div class="promo-card">
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem">
                    <span class="promo-badge">{p.tag}</span>
                    <span class="promo-title">{p.title}</span>
                </div>
                <p class="promo-desc">{p.description or ''}</p>
            </div>
            """
        
        # HTML для акций на мобилках
        promos_mobile = ""
        for p in promotions:
            promos_mobile += f'<span class="promo-chip">{p.tag} — {p.title}</span>'
        
        # Услуги (чипсы) — пока захардкожены, потом можно будет брать из БД
        services_chips = ""
        if "барбер" in (s.description or "").lower() or "стрижк" in (s.description or "").lower():
            services_chips += '<span class="service-chip">Стрижки</span>'
        if "бород" in (s.description or "").lower():
            services_chips += '<span class="service-chip">Борода</span>'
        if not services_chips:
            services_chips = '<span class="service-chip">Услуги</span>'
        
        salon_cards += f"""
        <div class="salon-card">
            <div class="salon-card-inner">
                <div class="salon-image">
                    <img src="{s.logo_url or '/static/default-salon.jpg'}" alt="{s.name}">
                    <button class="favorite-btn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"></path></svg>
                    </button>
                </div>
                <div class="salon-info">
                    <div>
                        <h3 class="salon-name">{s.name}</h3>
                        <p class="salon-address">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"></path><circle cx="12" cy="10" r="3"></circle></svg>
                            {s.address or 'Адрес не указан'}
                        </p>
                    </div>
                    <div class="salon-rating">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="var(--color-primary)" stroke="var(--color-primary)" stroke-width="2"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
                        <span class="rating-value">{s.rating or '0.0'}</span>
                        <span class="rating-count">({s.reviews_count or 0} отзывов)</span>
                    </div>
                    <p class="salon-desc">{s.description or ''}</p>
                    <div class="services-chips">
                        {services_chips}
                    </div>
                    <a href="/salons/{s.id}" class="btn-primary salon-btn">Смотреть мастеров →</a>
                </div>
                <div class="salon-promos-desktop">
                    <p class="promos-title">Акции</p>
                    {promos_desktop or '<p class="promo-desc">Пока нет акций</p>'}
                </div>
                <div class="salon-promos-mobile">
                    {promos_mobile}
                </div>
            </div>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Салоны — руми</title>
    {get_base_styles()}
    <style>
        /* Стили страницы салонов (как в салоны.txt) */
        .salon-card {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 1rem;
            overflow: hidden;
            margin-bottom: 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            transition: box-shadow 0.2s;
        }}
        .salon-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }}
        .salon-card-inner {{
            display: flex;
            flex-direction: column;
        }}
        @media (min-width: 640px) {{
            .salon-card-inner {{
                flex-direction: row;
            }}
        }}
        .salon-image {{
            position: relative;
            width: 100%;
            height: 10rem;
            flex-shrink: 0;
            overflow: hidden;
        }}
        @media (min-width: 640px) {{
            .salon-image {{
                width: 12rem;
                height: auto;
            }}
        }}
        .salon-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .favorite-btn {{
            position: absolute;
            right: 0.5rem;
            top: 0.5rem;
            display: flex;
            width: 2rem;
            height: 2rem;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: rgba(255,255,255,0.9);
            border: none;
            cursor: pointer;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            backdrop-filter: blur(4px);
            color: #9ca3af;
            transition: transform 0.2s;
        }}
        .favorite-btn:hover {{
            transform: scale(1.1);
        }}
        .salon-info {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 0.75rem;
            padding: 1.5rem;
        }}
        .salon-name {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--color-heading);
        }}
        .salon-address {{
            display: flex;
            align-items: center;
            gap: 0.25rem;
            color: var(--color-muted);
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }}
        .salon-address svg {{
            color: var(--color-primary);
        }}
        .salon-rating {{
            display: flex;
            align-items: center;
            gap: 0.375rem;
        }}
        .rating-value {{
            font-weight: 500;
            color: var(--color-heading);
            font-size: 0.875rem;
        }}
        .rating-count {{
            color: var(--color-muted);
            font-size: 0.875rem;
        }}
        .salon-desc {{
            color: var(--color-body);
            font-size: 0.875rem;
        }}
        .services-chips {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            padding-top: 0.25rem;
        }}
        .service-chip {{
            background: var(--color-accent-light);
            border-radius: 2rem;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--color-heading);
        }}
        .salon-btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--color-accent);
            color: white;
            padding: 0.5rem 1.25rem;
            border-radius: 2rem;
            font-size: 0.875rem;
            font-weight: 500;
            text-decoration: none;
            transition: opacity 0.2s;
            width: fit-content;
            margin-top: 0.5rem;
        }}
        .salon-btn:hover {{
            opacity: 0.9;
        }}
        .salon-promos-desktop {{
            display: none;
            flex-shrink: 0;
            border-left: 1px solid var(--color-border);
            padding: 1.25rem;
            width: 16rem;
            flex-direction: column;
            justify-content: center;
            gap: 0.75rem;
        }}
        @media (min-width: 1024px) {{
            .salon-promos-desktop {{
                display: flex;
            }}
        }}
        .promos-title {{
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--color-muted);
        }}
        .promo-card {{
            border: 1px solid var(--color-border);
            border-radius: 0.75rem;
            padding: 0.75rem;
            background: var(--color-surface-alt);
        }}
        .promo-badge {{
            display: inline-block;
            border-radius: 2rem;
            padding: 0.125rem 0.5rem;
            font-size: 0.625rem;
            font-weight: 700;
            color: white;
            background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
        }}
        .promo-title {{
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--color-heading);
        }}
        .promo-desc {{
            font-size: 0.6875rem;
            color: var(--color-muted);
            line-height: 1.4;
        }}
        .salon-promos-mobile {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            border-top: 1px solid var(--color-border);
            padding: 0.75rem 1.5rem;
        }}
        @media (min-width: 1024px) {{
            .salon-promos-mobile {{
                display: none;
            }}
        }}
        .promo-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.375rem;
            border-radius: 2rem;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            font-weight: 600;
            color: white;
            background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
        }}
        .page-header {{
            text-align: center;
            max-width: 42rem;
            margin: 0 auto 3rem;
        }}
        .page-header h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        .page-header p {{
            font-size: 1.1rem;
            color: var(--color-muted);
            margin-bottom: 2rem;
        }}
        .search-box {{
            position: relative;
            max-width: 32rem;
            margin: 0 auto;
        }}
        .search-box svg {{
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--color-muted);
            width: 1.25rem;
            height: 1.25rem;
        }}
        .search-box input {{
            width: 100%;
            padding: 0.875rem 1rem 0.875rem 3rem;
            border: 1px solid var(--color-border);
            border-radius: 2rem;
            font-size: 0.875rem;
            background: var(--color-surface);
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-box input:focus {{
            border-color: var(--color-accent);
        }}
    </style>
</head>
<body>
    {render_header("salons", user)}
    {render_sidebar("salons")}
    
    <main style="margin-right: 16rem;">
        <section class="section-py bg-surface-alt">
            <div class="section-container">
                <div class="page-header">
                    <h1 class="text-display">Салоны красоты</h1>
                    <p>Найдите лучший салон рядом с вами по названию или услуге</p>
                    <div class="search-box">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.34-4.34"></path></svg>
                        <input type="text" placeholder="Поиск салона по названию..." oninput="filterSalons(this.value)">
                    </div>
                </div>
                
                <div id="salons-list">
                    {salon_cards or '<div class="salon-card" style="padding:3rem;text-align:center"><p class="text-muted">Пока нет салонов. <a href="/register">Зарегистрируйтесь</a> как владелец, чтобы добавить первый салон!</p></div>'}
                </div>
            </div>
        </section>
        
        {render_footer()}
    </main>
    
    <script>
        function filterSalons(query) {{
            const cards = document.querySelectorAll('.salon-card');
            const lower = query.toLowerCase();
            cards.forEach(card => {{
                const name = card.querySelector('.salon-name')?.textContent.toLowerCase() || '';
                const desc = card.querySelector('.salon-desc')?.textContent.toLowerCase() || '';
                if (name.includes(lower) || desc.includes(lower)) {{
                    card.style.display = '';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>"""
    
    return html