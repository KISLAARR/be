# app/api/v1/endpoints/master.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import User, Master, Booking, UserRole
from app.api.deps import get_current_user, require_role

router = APIRouter()

@router.get("/schedule")
async def get_my_schedule(
    current_user: User = Depends(require_role([UserRole.MASTER])),
    db: AsyncSession = Depends(get_db)
):
    """Получить своё расписание (только для MASTER)"""
    
    # Находим профиль мастера
    result = await db.execute(
        select(Master).where(Master.user_id == current_user.id)
    )
    master = result.scalar_one_or_none()
    
    if not master:
        raise HTTPException(status_code=404, detail="Профиль мастера не найден")
    
    # Получаем все записи к этому мастеру
    bookings_result = await db.execute(
        select(Booking)
        .where(
            Booking.master_id == master.id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
        .order_by(Booking.start_time)
    )
    bookings = bookings_result.scalars().all()
    
    return {
        "master_id": master.id,
        "specialization": master.specialization,
        "bookings": [
            {
                "id": b.id,
                "start_time": b.start_time.isoformat(),
                "end_time": b.end_time.isoformat(),
                "status": b.status.value,
                "client_name": f"Клиент #{b.client_id}"
            }
            for b in bookings
        ]
    }