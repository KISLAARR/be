# app/api/v1/endpoints/bookings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from typing import List

from app.db.session import get_db
from app.models.models import Booking, Master, Service, User, BookingStatus
from app.schemas.booking import BookingCreate, BookingResponse, BookingCancel
from app.api.deps import get_current_user
from app.services.booking_service import BookingService

router = APIRouter()

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новую запись"""
    
    # Получаем услугу
    service_result = await db.execute(
        select(Service).where(Service.id == booking_data.service_id)
    )
    service = service_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    # Проверяем, что услуга принадлежит указанному мастеру
    if service.master_id != booking_data.master_id:
        raise HTTPException(status_code=400, detail="Услуга не принадлежит этому мастеру")
    
    # Проверяем доступность слота
    is_available = await BookingService.is_slot_available(
        db,
        booking_data.master_id,
        booking_data.start_time,
        service.duration_minutes
    )
    
    if not is_available:
        raise HTTPException(status_code=409, detail="Это время уже занято")
    
    # Рассчитываем цену
    final_price = await BookingService.calculate_price(current_user, service)
    
    # Создаём запись
    end_time = booking_data.start_time + timedelta(minutes=service.duration_minutes)
    
    booking = Booking(
        client_id=current_user.id,
        master_id=booking_data.master_id,
        service_id=booking_data.service_id,
        start_time=booking_data.start_time,
        end_time=end_time,
        status=BookingStatus.PENDING,
        final_price=final_price
    )
    
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    
    return booking

@router.get("/my", response_model=List[BookingResponse])
async def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список моих записей"""
    
    result = await db.execute(
        select(Booking)
        .where(Booking.client_id == current_user.id)
        .order_by(Booking.start_time.desc())
    )
    bookings = result.scalars().all()
    
    return bookings

@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    cancel_data: BookingCancel,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Отменить запись"""
    
    result = await db.execute(
        select(Booking).where(
            Booking.id == booking_id,
            Booking.client_id == current_user.id
        )
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Запись уже отменена")
    
    if booking.status == BookingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Нельзя отменить выполненную запись")
    
    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(booking)
    
    return booking