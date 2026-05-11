# app/api/v1/endpoints/business.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.models.models import User, Salon, Master, Booking, UserRole
from app.api.deps import get_current_user, require_role

router = APIRouter()

@router.get("/dashboard")
async def business_dashboard(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OWNER])),
    db: AsyncSession = Depends(get_db)
):
    """Панель управления салоном (только для ADMIN и OWNER)"""
    
    # Если у пользователя есть привязанный салон — используем его
    salon_id = current_user.managed_salon_id
    
    if not salon_id:
        # Если админ не привязан к салону, ищем первый активный салон
        result = await db.execute(select(Salon).where(Salon.is_active == True).limit(1))
        salon = result.scalar_one_or_none()
        if not salon:
            raise HTTPException(status_code=404, detail="Салоны не найдены")
        salon_id = salon.id
    else:
        result = await db.execute(select(Salon).where(Salon.id == salon_id))
        salon = result.scalar_one_or_none()
    
    # Статистика салона
    masters_count_result = await db.execute(
        select(Master).where(Master.salon_id == salon_id, Master.is_active == True)
    )
    masters = masters_count_result.scalars().all()
    
    bookings_result = await db.execute(
        select(Booking).where(Booking.master_id.in_([m.id for m in masters]))
    )
    bookings = bookings_result.scalars().all()
    
    return {
        "salon": {
            "id": salon.id,
            "name": salon.name,
            "address": salon.address,
            "rating": salon.rating
        },
        "stats": {
            "masters_count": len(masters),
            "bookings_count": len(bookings),
            "role": current_user.role.value
        },
        "message": f"Добро пожаловать, {current_user.full_name or 'Администратор'}!"
    }

@router.get("/masters")
async def get_salon_masters(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OWNER])),
    db: AsyncSession = Depends(get_db)
):
    """Получить список мастеров салона (только для ADMIN и OWNER)"""
    
    salon_id = current_user.managed_salon_id
    if not salon_id:
        result = await db.execute(select(Salon).where(Salon.is_active == True).limit(1))
        salon = result.scalar_one_or_none()
        if not salon:
            raise HTTPException(status_code=404, detail="Салоны не найдены")
        salon_id = salon.id
    
    result = await db.execute(
        select(Master).where(Master.salon_id == salon_id, Master.is_active == True)
    )
    masters = result.scalars().all()
    
    return [
        {
            "id": m.id,
            "name": m.user.full_name if m.user else "Не указано",
            "specialization": m.specialization,
            "rating": m.rating,
            "experience_years": m.experience_years
        }
        for m in masters
    ]