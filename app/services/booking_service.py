# app/services/booking_service.py
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.models import Booking, Master, Service, BookingStatus

class BookingService:
    
    # Время перерыва между записями (в минутах)
    DEFAULT_BREAK_MINUTES = 15
    
    @staticmethod
    async def get_booked_slots(
        db: AsyncSession,
        master_id: int,
        date: datetime
    ) -> list[tuple[datetime, datetime]]:
        """
        Возвращает список занятых интервалов (start, end) для мастера на конкретный день.
        Каждый интервал включает время услуги + перерыв после неё.
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        result = await db.execute(
            select(Booking).where(
                Booking.master_id == master_id,
                Booking.start_time >= start_of_day,
                Booking.start_time < end_of_day,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            ).order_by(Booking.start_time)
        )
        bookings = result.scalars().all()
        
        slots = []
        for b in bookings:
            # Интервал: от начала записи до конца + перерыв
            end_with_break = b.end_time + timedelta(minutes=BookingService.DEFAULT_BREAK_MINUTES)
            slots.append((b.start_time, end_with_break))
        
        return slots
    
    @staticmethod
    async def is_slot_available(
        db: AsyncSession,
        master_id: int,
        start_time: datetime,
        duration_minutes: int
    ) -> bool:
        """
        Проверяет, свободен ли слот у мастера.
        Учитывает:
        - Длительность услуги (start_time → end_time)
        - Перерыв после занятых записей (end_time + 15 мин)
        - Наложения по времени
        """
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Ищем ВСЕ записи, которые пересекаются с нашим слотом
        # Пересечение = наша запись начинается ДО конца существующей + перерыв
        # И наша запись заканчивается ПОСЛЕ начала существующей
        result = await db.execute(
            select(Booking).where(
                Booking.master_id == master_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                # Условие пересечения
                Booking.start_time < end_time,
                Booking.end_time + timedelta(minutes=BookingService.DEFAULT_BREAK_MINUTES) > start_time
            )
        )
        existing = result.scalars().all()
        
        # Если есть пересекающиеся записи — слот занят
        if len(existing) > 0:
            return False
        
        # Проверяем, что слот в рабочие часы (10:00-20:00)
        work_start = start_time.replace(hour=10, minute=0, second=0, microsecond=0)
        work_end = start_time.replace(hour=20, minute=0, second=0, microsecond=0)
        
        if start_time < work_start or end_time > work_end:
            return False
        
        return True
    
    @staticmethod
    async def calculate_price(user: 'User', service: 'Service') -> int:
        """Рассчитывает цену с учётом подписки модели"""
        base_price = service.price
        discount = 0
        
        if user.subscription_tier and user.subscription_expires_at:
            if user.subscription_expires_at > datetime.now():
                discount_map = {
                    'start': 30,
                    'pro': 50,
                    'premium': 70
                }
                tier = user.subscription_tier
                if hasattr(tier, 'value'):
                    tier = tier.value
                discount_percent = discount_map.get(tier, 0)
                discount = int(base_price * discount_percent / 100)
        
        return base_price - discount