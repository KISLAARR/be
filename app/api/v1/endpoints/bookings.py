# app/api/v1/endpoints/bookings.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import timedelta, datetime, timezone as tz
from typing import List
import json

from app.db.session import get_db
from app.models.models import Booking, Master, Service, User, BookingStatus, Review, Salon
from app.schemas.booking import BookingCreate, BookingResponse, BookingCancel
from app.api.deps import get_current_user
from app.services.booking_service import BookingService
from app.utils.timezone import get_salon_time

router = APIRouter()

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новую запись."""
    service_result = await db.execute(select(Service).where(Service.id == booking_data.service_id))
    service = service_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    
    if service.master_id != booking_data.master_id:
        raise HTTPException(status_code=400, detail="Услуга не принадлежит этому мастеру")
    
    now = datetime.now()
    if booking_data.start_time.replace(tzinfo=None) < now:
        raise HTTPException(status_code=400, detail="Нельзя записаться на прошедшее время.")
    
    is_available = await BookingService.is_slot_available(
        db, booking_data.master_id,
        booking_data.start_time.replace(tzinfo=None),
        service.duration_minutes
    )
    
    if not is_available:
        raise HTTPException(status_code=409, detail="Это время уже занято")
    
    final_price = await BookingService.calculate_price(current_user, service)
    start_time = booking_data.start_time.replace(tzinfo=None)
    end_time = start_time + timedelta(minutes=service.duration_minutes)
    
    booking = Booking(
        client_id=current_user.id,
        master_id=booking_data.master_id,
        service_id=booking_data.service_id,
        start_time=start_time.replace(tzinfo=None),
        end_time=end_time.replace(tzinfo=None),
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
    result = await db.execute(
        select(Booking).where(Booking.client_id == current_user.id).order_by(Booking.start_time.asc())
    )
    return result.scalars().all()

@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    cancel_data: BookingCancel,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Booking).where(Booking.id == booking_id, Booking.client_id == current_user.id))
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
    date: str,
    service_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Возвращает доступные слоты с учётом графика салона, услуги и перерыва."""
    
    master = (await db.execute(select(Master).where(Master.id == master_id))).scalar_one_or_none()
    if not master:
        return {"slots": [], "message": "Мастер не найден"}
    
    service = (await db.execute(select(Service).where(Service.id == service_id))).scalar_one_or_none()
    if not service:
        return {"slots": [], "message": "Услуга не найдена"}
    
    salon = (await db.execute(select(Salon).where(Salon.id == master.salon_id))).scalar_one_or_none()
    if not salon or not salon.working_hours:
        return {"slots": [], "message": "График работы салона не задан"}
    
    try:
        working_hours = json.loads(salon.working_hours)
    except:
        return {"slots": [], "message": "Ошибка в графике салона"}
    
    try:
        target_date = datetime.fromisoformat(date)
    except:
        target_date = datetime.now()
    
    day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    day_name = day_names[target_date.weekday()]
    
    if day_name not in working_hours or working_hours[day_name] in ("выходной", "closed", "day off"):
        return {"slots": [], "message": f"Салон не работает в этот день ({day_name})"}
    
    time_range = working_hours[day_name]
    try:
        start_str, end_str = time_range.split("-")
        work_start_h, work_start_m = map(int, start_str.split(":"))
        work_end_h, work_end_m = map(int, end_str.split(":"))
    except:
        return {"slots": [], "message": "Ошибка в графике салона"}
    
    work_start = target_date.replace(hour=work_start_h, minute=work_start_m, second=0, microsecond=0)
    work_end = target_date.replace(hour=work_end_h, minute=work_end_m, second=0, microsecond=0)
    
    slot_duration = service.duration_minutes + master.break_minutes
    
    booked = await db.execute(
        select(Booking).where(
            Booking.master_id == master_id,
            Booking.start_time >= work_start,
            Booking.start_time < work_end,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        ).order_by(Booking.start_time)
    )
    booked_slots = booked.scalars().all()
    
    now = get_salon_time(salon.timezone or "Europe/Moscow")
    now = now.replace(tzinfo=None)
    
    slots = []
    current = work_start
    
    while current + timedelta(minutes=slot_duration) <= work_end:
        slot_end = current + timedelta(minutes=slot_duration)
        
        if current < now:
            current += timedelta(minutes=slot_duration)
            continue
        
        is_free = True
        for b in booked_slots:
            b_start = b.start_time.replace(tzinfo=None) if b.start_time.tzinfo else b.start_time
            b_end = b.end_time.replace(tzinfo=None) if b.end_time.tzinfo else b.end_time
            if current < b_end and slot_end > b_start:
                is_free = False
                break
        
        if is_free:
            slots.append(current.strftime("%Y-%m-%dT%H:%M"))
        
        current += timedelta(minutes=slot_duration)
    
    return {
        "date": date,
        "slots": slots,
        "service_duration": service.duration_minutes,
        "break": master.break_minutes,
        "total_slot": slot_duration
    }

@router.get("/master-schedule", response_model=List[BookingResponse])
async def get_master_schedule(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role.value != "master":
        raise HTTPException(status_code=403, detail="Только мастер может просматривать расписание")
    result = await db.execute(select(Master).where(Master.user_id == current_user.id))
    master = result.scalar_one_or_none()
    if not master:
        raise HTTPException(status_code=404, detail="Профиль мастера не найден")
    bookings_result = await db.execute(
        select(Booking).where(
            Booking.master_id == master.id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        ).order_by(Booking.start_time.asc())
    )
    return bookings_result.scalars().all()

@router.post("/bookings", response_class=HTMLResponse)
async def create_booking_web(
    request: Request,
    master_id: int = Form(...),
    start_time: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    from app.web.auth import get_current_user_from_cookie
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    result = await db.execute(select(Master).where(Master.id == master_id))
    master = result.scalar_one_or_none()
    if not master:
        return HTMLResponse(content="<h1>Мастер не найден</h1>", status_code=404)
    svc_result = await db.execute(select(Service).where(Service.master_id == master_id).limit(1))
    service = svc_result.scalar_one_or_none()
    if not service:
        return HTMLResponse(content="<h1>У мастера пока нет услуг</h1>", status_code=400)
    try:
        start = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
        end = start + timedelta(minutes=service.duration_minutes)
    except:
        return HTMLResponse(content="<h1>Неверный формат даты</h1>", status_code=400)
    booking = Booking(
        client_id=user.id, master_id=master_id, service_id=service.id,
        start_time=start, end_time=end, status=BookingStatus.PENDING, final_price=service.price
    )
    db.add(booking)
    await db.commit()
    return RedirectResponse(url="/bookings?success=1", status_code=302)

@router.post("/confirm")
async def confirm_booking_web(
    request: Request,
    master_id: int = Form(...),
    service_id: int = Form(...),
    start_time: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    from app.web.auth import get_current_user_from_cookie
    
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    service = (await db.execute(select(Service).where(Service.id == service_id))).scalar_one_or_none()
    if not service:
        return HTMLResponse(content="<h1>Услуга не найдена</h1>", status_code=404)
    
    try:
        start = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
        end = start + timedelta(minutes=service.duration_minutes)
    except:
        return HTMLResponse(content="<h1>Неверный формат даты</h1>", status_code=400)
    
    # ===== ПРОВЕРКА 1: Нельзя записаться на то же время в любой салон =====
    duplicate = await db.execute(
        select(Booking).where(
            Booking.client_id == user.id,
            Booking.start_time == start,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
    )
    if duplicate.scalar_one_or_none():
        return HTMLResponse(content="""
        <!DOCTYPE html><html><body style="text-align:center;padding:3rem;font-family:sans-serif">
        <h2 style="color:#e53e3e">⚠️ Вы уже записаны</h2>
        <p>У вас уже есть запись на это время в другой салон.</p>
        <a href="/bookings" style="color:#F28C6F">Мои записи</a> · 
        <a href="/salons" style="color:#F28C6F">Назад к салонам</a>
        </body></html>""", status_code=409)
    
    # ===== ПРОВЕРКА 2: Не больше 5 предстоящих записей =====
    active_count = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.client_id == user.id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            Booking.start_time > datetime.now()
        )
    )
    #if active_count.scalar() >= 5:
        #return HTMLResponse(content="""
        #<!DOCTYPE html><html><body style="text-align:center;padding:3rem;font-family:sans-serif">
        #<h2 style="color:#e53e3e">⚠️ Слишком много записей</h2>
        #<p>У вас уже 5 активных записей. Отмените ненужные, чтобы записаться снова.</p>
        #<a href="/bookings" style="color:#F28C6F">Мои записи</a>
        #</body></html>""", status_code=429)
    
    # ===== ПРОВЕРКА 3: Слот ещё свободен =====
    conflict = await db.execute(
        select(Booking).where(
            Booking.master_id == master_id,
            Booking.start_time < end,
            Booking.end_time > start,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
    )
    if conflict.scalar_one_or_none():
        return HTMLResponse(content="""
        <!DOCTYPE html><html><body style="text-align:center;padding:3rem;font-family:sans-serif">
        <h2 style="color:#e53e3e">⚠️ Время занято</h2>
        <p>Кто-то уже записался на это время. Выберите другой слот.</p>
        <a href="javascript:history.back()" style="color:#F28C6F">← Назад</a>
        </body></html>""", status_code=409)
    
    booking = Booking(
        client_id=user.id, master_id=master_id, service_id=service_id,
        start_time=start, end_time=end, status=BookingStatus.PENDING, final_price=service.price
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
    from app.web.auth import get_current_user_from_cookie
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    if rating < 1 or rating > 5:
        return HTMLResponse(content="<h1>Оценка должна быть от 1 до 5</h1>", status_code=400)
    review = Review(client_id=user.id, master_id=master_id, salon_id=salon_id, rating=rating, comment=comment)
    db.add(review)
    master = (await db.execute(select(Master).where(Master.id == master_id))).scalar_one_or_none()
    if master:
        avg_result = await db.execute(select(func.avg(Review.rating)).where(Review.master_id == master_id))
        master.rating = round(float(avg_result.scalar() or 0.0), 1)
    salon = (await db.execute(select(Salon).where(Salon.id == salon_id))).scalar_one_or_none()
    if salon:
        salon.reviews_count = (salon.reviews_count or 0) + 1
        avg_result = await db.execute(select(func.avg(Review.rating)).where(Review.salon_id == salon_id))
        salon.rating = round(float(avg_result.scalar() or 0.0), 1)
    await db.commit()
    return RedirectResponse(url=f"/salons/{salon_id}?reviewed=1", status_code=302)