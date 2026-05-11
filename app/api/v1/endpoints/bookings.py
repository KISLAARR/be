# app/api/v1/endpoints/bookings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta, datetime, timezone
from typing import List

from app.db.session import get_db
from app.models.models import Booking, Master, Service, User, BookingStatus
from app.schemas.booking import BookingCreate, BookingResponse, BookingCancel
from app.api.deps import get_current_user
from app.services.booking_service import BookingService

router = APIRouter()

# Московский часовой пояс (UTC+3)
MSK = timezone(timedelta(hours=3))

def to_msk(dt: datetime) -> datetime:
    """Приводит время к московскому, если оно без часового пояса"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=MSK)
    return dt

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новую запись. Один слот = один клиент."""
    
    # 1. Получаем услугу
    service_result = await db.execute(
        select(Service).where(Service.id == booking_data.service_id)
    )
    service = service_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    # 2. Проверяем, что услуга принадлежит мастеру
    if service.master_id != booking_data.master_id:
        raise HTTPException(status_code=400, detail="Услуга не принадлежит этому мастеру")
    
    # 3. Приводим время к MSK и проверяем, что оно в будущем
    start_time = to_msk(booking_data.start_time)
    now_msk = datetime.now(MSK)
    
    if start_time < now_msk + timedelta(hours=1):
        raise HTTPException(
            status_code=400, 
            detail="Нельзя записаться на прошедшее время. Выберите время не ранее чем через 1 час."
        )
    
    # 4. Проверяем доступность слота
    is_available = await BookingService.is_slot_available(
        db,
        booking_data.master_id,
        start_time,
        service.duration_minutes
    )
    
    if not is_available:
        raise HTTPException(
            status_code=409, 
            detail="Это время уже занято или попадает в технологический перерыв"
        )
    
    # 5. Рассчитываем цену
    final_price = await BookingService.calculate_price(current_user, service)
    
    # 6. Вычисляем конец процедуры
    end_time = start_time + timedelta(minutes=service.duration_minutes)
    
    # 7. Создаём запись (сохраняем в UTC для БД)
    booking = Booking(
        client_id=current_user.id,
        master_id=booking_data.master_id,
        service_id=booking_data.service_id,
        start_time=start_time.astimezone(timezone.utc).replace(tzinfo=None),
        end_time=end_time.astimezone(timezone.utc).replace(tzinfo=None),
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
        .order_by(Booking.start_time.asc())
    )
    bookings = result.scalars().all()
    
    # Переводим время из UTC в MSK для отображения
    for b in bookings:
        if b.start_time.tzinfo is None:
            b.start_time = b.start_time.replace(tzinfo=timezone.utc)
        if b.end_time.tzinfo is None:
            b.end_time = b.end_time.replace(tzinfo=timezone.utc)
        b.start_time = b.start_time.astimezone(MSK)
        b.end_time = b.end_time.astimezone(MSK)
    
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

@router.get("/available/{master_id}")
async def get_available_slots(
    master_id: int,
    date: datetime,
    db: AsyncSession = Depends(get_db)
):
    """Возвращает список доступных слотов для мастера на дату"""
    slots = []
    now_msk = datetime.now(MSK)
    
    # Приводим дату к MSK
    date_msk = to_msk(date)
    
    if date_msk.date() < now_msk.date():
        return {"date": date_msk.strftime("%Y-%m-%d"), "slots": [], "message": "Эта дата уже прошла"}
    
    work_start = date_msk.replace(hour=10, minute=0, second=0, microsecond=0)
    work_end = date_msk.replace(hour=20, minute=0, second=0, microsecond=0)
    
    booked = await BookingService.get_booked_slots(db, master_id, date_msk)
    
    current = work_start
    while current + timedelta(minutes=30) <= work_end:
        slot_end = current + timedelta(minutes=30)
        
        if current < now_msk and date_msk.date() == now_msk.date():
            current += timedelta(minutes=30)
            continue
        
        is_free = True
        for b_start, b_end in booked:
            if current < b_end and slot_end > b_start:
                is_free = False
                break
        
        if is_free:
            slots.append(current.isoformat())
        
        current += timedelta(minutes=30)
    
    return {"date": date_msk.strftime("%Y-%m-%d"), "slots": slots}

@router.get("/master-schedule", response_model=List[BookingResponse])
async def get_master_schedule(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить расписание мастера"""
    if current_user.role.value != "master":
        raise HTTPException(status_code=403, detail="Только мастер может просматривать расписание")
    
    result = await db.execute(
        select(Master).where(Master.user_id == current_user.id)
    )
    master = result.scalar_one_or_none()
    
    if not master:
        raise HTTPException(status_code=404, detail="Профиль мастера не найден")
    
    bookings_result = await db.execute(
        select(Booking)
        .where(
            Booking.master_id == master.id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
        .order_by(Booking.start_time.asc())
    )
    bookings = bookings_result.scalars().all()
    
    return bookings