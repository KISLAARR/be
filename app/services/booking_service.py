# app/services/booking_service.py
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.models import Booking, Master, Service, Schedule, BookingStatus
from app.models.models import User, SubscriptionTier

class BookingService:
    
    SUBSCRIPTION_DISCOUNTS = {
        SubscriptionTier.START: 30,
        SubscriptionTier.PRO: 50,
        SubscriptionTier.PREMIUM: 70,
    }
    
    @staticmethod
    async def is_slot_available(
        db: AsyncSession,
        master_id: int,
        start_time: datetime,
        duration_minutes: int
    ) -> bool:
        """Проверяет, свободен ли слот у мастера"""
        
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Проверяем, есть ли пересекающиеся записи
        result = await db.execute(
            select(Booking).where(
                Booking.master_id == master_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                and_(
                    Booking.start_time < end_time,
                    Booking.end_time > start_time
                )
            )
        )
        existing = result.scalars().all()
        
        return len(existing) == 0
    
    @staticmethod
    async def calculate_price(
        user: User,
        service: Service
    ) -> int:
        """Рассчитывает цену с учётом подписки модели"""
        base_price = service.price
        discount = 0
        
        if user.subscription_tier and user.subscription_expires_at:
            if user.subscription_expires_at > datetime.now():
                discount_percent = BookingService.SUBSCRIPTION_DISCOUNTS.get(
                    user.subscription_tier, 0
                )
                discount = int(base_price * discount_percent / 100)
        
        return base_price - discount