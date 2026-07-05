# app/web/pages/bookings.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.models.models import Booking, BookingStatus, Master, Service, Salon, User
from app.web.components.header import render_header
from app.web.components.footer import render_footer
from app.web.components.sidebar import render_sidebar
from app.web.components.styles import get_base_styles
from datetime import timedelta

async def render_bookings_page(db: AsyncSession, user) -> str:
    """Страница 'Мои записи' для клиента."""
    
    # Получаем все записи пользователя
    bookings_result = await db.execute(
        select(Booking).where(
            Booking.client_id == user.id
        ).order_by(Booking.start_time.desc())
    )
    bookings = bookings_result.scalars().all()
    
<<<<<<< HEAD
    # Разделяем на предстоящие и завершённые
    now = datetime.now(timezone.utc)
=======
    # Разделяем на предстоящие и завершённые.
    # Брони хранятся naive (DateTime timezone=False) → сравниваем с naive now,
    # иначе TypeError: can't compare offset-naive and offset-aware datetimes.
    now = datetime.now()
>>>>>>> main
    upcoming = [b for b in bookings if b.start_time > now and b.status not in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]]
    completed = [b for b in bookings if b.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED] or b.start_time <= now]
    
    async def render_booking_card(booking, is_upcoming=True):
        # Явно загружаем мастера
        master = None
        if booking.master_id:
            master = (await db.execute(select(Master).where(Master.id == booking.master_id))).scalar_one_or_none()
        
        # Явно загружаем услугу
        service = None
        if booking.service_id:
            service = (await db.execute(select(Service).where(Service.id == booking.service_id))).scalar_one_or_none()
        
        master_name = "Мастер"
        service_name = "Услуга"
        salon_name = "Салон"
        
        if master:
            master_user = (await db.execute(select(User).where(User.id == master.user_id))).scalar_one_or_none()
            master_name = master_user.full_name if master_user else "Мастер"
            if master.salon_id:
                salon = (await db.execute(select(Salon).where(Salon.id == master.salon_id))).scalar_one_or_none()
                salon_name = salon.name if salon else "Салон"
        
        if service:
            service_name = service.name
        
        status_label = {
            BookingStatus.PENDING: "⏳ Ожидает",
            BookingStatus.CONFIRMED: "✅ Подтверждено",
            BookingStatus.COMPLETED: "✔️ Завершено",
            BookingStatus.CANCELLED: "❌ Отменено",
        }.get(booking.status, "—")
        
        cancel_btn = ""
        if is_upcoming and booking.status != BookingStatus.CANCELLED:
            cancel_btn = f'<button class="btn-outline" style="color:red;border-color:red;margin-top:0.5rem;font-size:0.8rem;padding:0.4rem 0.8rem" onclick="cancelBooking({booking.id})">Отменить</button>'
        
        return f"""
        <div class="booking-card">
            <div class="booking-header">
                <h3>{service_name}</h3>
                <span class="booking-status">{status_label}</span>
            </div>
            <div class="booking-body">
                <p><strong>📅 Дата:</strong> {booking.start_time.replace(tzinfo=None).strftime('%d.%m.%Y в %H:%M')}</p>
                <p><strong>💇 Мастер:</strong> {master_name}</p>
                <p><strong>🏢 Салон:</strong> {salon_name}</p>
                <p><strong>💰 Цена:</strong> {booking.final_price or '—'} ₽</p>
            </div>
            {cancel_btn}
        </div>
        """
    
    # Собираем карточки с await
    upcoming_cards = ""
    for b in upcoming:
        upcoming_cards += await render_booking_card(b, True)
    
    completed_cards = ""
    for b in completed:
        completed_cards += await render_booking_card(b, False)
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Мои записи — руми</title>
    {get_base_styles()}
    <style>
        .booking-card {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: box-shadow 0.2s;
        }}
        .booking-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .booking-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--color-border);
        }}
        .booking-header h3 {{
            font-size: 1.1rem;
            color: var(--color-heading);
        }}
        .booking-status {{
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            background: var(--color-accent-light);
            color: var(--color-primary);
        }}
        .booking-body p {{
            font-size: 0.9rem;
            color: var(--color-body);
            margin-bottom: 0.35rem;
        }}
        .empty-state {{
            text-align: center;
            padding: 3rem;
            color: var(--color-muted);
        }}
        .empty-state h3 {{
            font-size: 1.25rem;
            margin-bottom: 0.5rem;
            color: var(--color-heading);
        }}
    </style>
</head>
<body>
    {render_header("bookings", user)}
    {render_sidebar("bookings")}
    
    <main style="margin-right: 16rem; padding-top: 2rem;">
        <div class="section-container">
            <h1 class="text-display" style="font-size:2rem;margin-bottom:2rem">Мои записи</h1>
            
            <!-- Предстоящие -->
            <h2 class="text-subtitle" style="font-size:1.25rem;margin-bottom:1rem">📅 Предстоящие</h2>
            {upcoming_cards or '<div class="empty-state"><h3>Нет предстоящих записей</h3><p>Запишитесь в <a href="/salons">салон</a>, чтобы увидеть бронирования здесь.</p></div>'}
            
            <!-- Завершённые -->
            <h2 class="text-subtitle" style="font-size:1.25rem;margin:2rem 0 1rem">✔️ Завершённые</h2>
            {completed_cards or '<div class="empty-state"><p>Пока нет завершённых записей.</p></div>'}
        </div>
    </main>
    
    {render_footer()}
    
    <script>
        function cancelBooking(bookingId) {{
            if (confirm('Вы уверены, что хотите отменить запись?')) {{
                fetch('/api/v1/bookings/' + bookingId + '/cancel', {{ method: 'POST' }})
                    .then(r => r.json())
                    .then(data => {{
                        alert('Запись отменена');
                        location.reload();
                    }})
                    .catch(err => alert('Ошибка при отмене'));
            }}
        }}
    </script>
</body>
</html>"""
    
    return html