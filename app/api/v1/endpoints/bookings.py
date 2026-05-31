# app/api/v1/endpoints/bookings.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import timedelta, datetime
from typing import List

from app.db.session import get_db
from app.models.models import Booking, Master, Service, User, BookingStatus, Review, Salon
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
    """Создать новую запись. Время сохраняется КАК ЕСТЬ."""
    
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
    
    # 3. Проверяем, что время в будущем (относительно текущего локального времени)
    now = datetime.now()
    if booking_data.start_time.replace(tzinfo=None) < now:
        raise HTTPException(
            status_code=400, 
            detail="Нельзя записаться на прошедшее время."
        )
    
    # 4. Проверяем доступность слота
    is_available = await BookingService.is_slot_available(
        db,
        booking_data.master_id,
        booking_data.start_time.replace(tzinfo=None),
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
    start_time = booking_data.start_time.replace(tzinfo=None)  # Убираем tzinfo, если есть
    end_time = start_time + timedelta(minutes=service.duration_minutes)
    
    # 7. Создаём запись (время КАК ЕСТЬ)
    booking = Booking(
        client_id=current_user.id,
        master_id=booking_data.master_id,
        service_id=booking_data.service_id,
        start_time=start_time.replace(tzinfo=None),    # ← чистое время без +03:00
        end_time=end_time.replace(tzinfo=None),        # ← чистое время без +03:00
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
    now = datetime.now()
    
    # Приводим дату к началу дня
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if date.date() < now.date():
        return {"date": date.strftime("%Y-%m-%d"), "slots": [], "message": "Эта дата уже прошла"}
    
    work_start = date.replace(hour=10, minute=0)
    work_end = date.replace(hour=20, minute=0)
    
    booked = await BookingService.get_booked_slots(db, master_id, date)
    
    current = work_start
    while current + timedelta(minutes=30) <= work_end:
        slot_end = current + timedelta(minutes=30)
        
        # Пропускаем прошедшие слоты (только для сегодняшней даты)
        if date.date() == now.date() and current < now:
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
    
    return {"date": date.strftime("%Y-%m-%d"), "slots": slots}

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

@router.post("/bookings", response_class=HTMLResponse)
async def create_booking_web(
    request: Request,
    master_id: int = Form(...),
    start_time: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Создание записи через веб-форму."""
    from app.web.auth import get_current_user_from_cookie
    
    # Получаем пользователя
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Получаем мастера
    result = await db.execute(select(Master).where(Master.id == master_id))
    master = result.scalar_one_or_none()
    if not master:
        return HTMLResponse(content="<h1>Мастер не найден</h1>", status_code=404)
    
    # Получаем первую услугу мастера (или можно передавать service_id)
    svc_result = await db.execute(
        select(Service).where(Service.master_id == master_id).limit(1)
    )
    service = svc_result.scalar_one_or_none()
    if not service:
        return HTMLResponse(content="<h1>У мастера пока нет услуг</h1>", status_code=400)
    
    # Парсим дату и время
    try:
        start = datetime.fromisoformat(start_time)
        end = start + timedelta(minutes=service.duration_minutes)
    except:
        return HTMLResponse(content="<h1>Неверный формат даты</h1>", status_code=400)
    
    # Создаём запись
    booking = Booking(
        client_id=user.id,
        master_id=master_id,
        service_id=service.id,
        start_time=start,
        end_time=end,
        status=BookingStatus.PENDING,
        final_price=service.price
    )
    db.add(booking)
    await db.commit()
    
    # Перенаправляем на страницу "Мои записи"
    return RedirectResponse(url="/bookings?success=1", status_code=302)

@router.post("/bookings/confirm")
async def confirm_booking_web(
    request: Request,
    master_id: int = Form(...),
    service_id: int = Form(...),
    start_time: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Подтверждение записи с выбранной услугой."""
    from app.web.auth import get_current_user_from_cookie
    
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Получаем услугу
    service = (await db.execute(select(Service).where(Service.id == service_id))).scalar_one_or_none()
    if not service:
        return HTMLResponse(content="<h1>Услуга не найдена</h1>", status_code=404)
    
    # Парсим время
    try:
        start = datetime.fromisoformat(start_time)
        end = start + timedelta(minutes=service.duration_minutes)
    except:
        return HTMLResponse(content="<h1>Неверный формат даты</h1>", status_code=400)
    
    # Создаём запись
    booking = Booking(
        client_id=user.id,
        master_id=master_id,
        service_id=service_id,
        start_time=start,
        end_time=end,
        status=BookingStatus.PENDING,
        final_price=service.price
    )
    db.add(booking)
    await db.commit()
    
    return RedirectResponse(url="/bookings?success=1", status_code=302)

@router.post("/reviews/create")
async def create_review_web(
    request: Request,
    master_id: int = Form(...),
    salon_id: int = Form(...),
    rating: int = Form(...),
    comment: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    """Создание отзыва с пересчётом рейтинга."""
    from app.web.auth import get_current_user_from_cookie
    
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if rating < 1 or rating > 5:
        return HTMLResponse(content="<h1>Оценка должна быть от 1 до 5</h1>", status_code=400)
    
    review = Review(
        client_id=user.id,
        master_id=master_id,
        salon_id=salon_id,
        rating=rating,
        comment=comment
    )
    db.add(review)
    
    # Пересчёт рейтинга мастера
    master = (await db.execute(select(Master).where(Master.id == master_id))).scalar_one_or_none()
    if master:
        avg_result = await db.execute(
            select(func.avg(Review.rating)).where(Review.master_id == master_id)
        )
        master.rating = round(float(avg_result.scalar() or 0.0), 1)
    
    # Пересчёт рейтинга салона
    salon = (await db.execute(select(Salon).where(Salon.id == salon_id))).scalar_one_or_none()
    if salon:
        salon.reviews_count = (salon.reviews_count or 0) + 1
        avg_result = await db.execute(
            select(func.avg(Review.rating)).where(Review.salon_id == salon_id)
        )
        salon.rating = round(float(avg_result.scalar() or 0.0), 1)
    
    await db.commit()
    
    return RedirectResponse(url=f"/salons/{salon_id}?reviewed=1", status_code=302)