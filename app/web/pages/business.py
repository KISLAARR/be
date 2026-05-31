# app/api/v1/endpoints/business.py
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.models.models import User, Salon, SalonPhoto, Master, Service, Promotion, UserRole
from app.schemas.business import (
    SalonUpdateRequest, 
    SalonResponse,
    MasterResponse,
    ServiceResponse,
    PromotionResponse
)
from app.api.deps import get_current_user

router = APIRouter()

# Вспомогательная функция для проверки прав
async def get_owner_salon(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Salon:
    """Проверяет, что пользователь — BUSINESS, и возвращает его салон."""
    if current_user.role != UserRole.BUSINESS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Этот раздел доступен только владельцам салонов"
        )
    
    result = await db.execute(
        select(Salon).where(Salon.owner_id == current_user.id)
    )
    salon = result.scalar_one_or_none()
    
    if not salon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У вас пока нет привязанного салона. Заполните заявку на подключение."
        )
    
    return salon


# ========== НОВЫЙ POST-эндпоинт для создания салона ==========
@router.post("/my-salon")
async def create_my_salon(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    address: str = Form(...),
    phone: str = Form(...),
    latitude: str = Form(""),
    longitude: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    """Создание нового салона владельцем через веб-форму."""
    from app.web.auth import get_current_user_from_cookie
    
    # Получаем пользователя из куки
    user = await get_current_user_from_cookie(request, db)
    if not user or user.role.value != "business":
        return RedirectResponse(url="/login", status_code=302)
    
    # Проверяем, нет ли уже салона у этого владельца
    existing = (await db.execute(select(Salon).where(Salon.owner_id == user.id))).scalar_one_or_none()
    if existing:
        return RedirectResponse(url="/business/dashboard", status_code=302)
    
    # Создаём салон
    salon = Salon(
        owner_id=user.id,
        name=name,
        description=description,
        address=address,
        phone=phone,
        latitude=float(latitude) if latitude else 55.7558,
        longitude=float(longitude) if longitude else 37.6173,
        rating=0.0,
        reviews_count=0,
        is_active=True
    )
    db.add(salon)
    await db.commit()
    await db.refresh(salon)
    
    # После успешного создания — перенаправляем в бизнес-панель
    return RedirectResponse(url="/business/dashboard?success=1", status_code=302)


@router.get("/my-salon", response_model=SalonResponse)
async def get_my_salon(
    salon: Salon = Depends(get_owner_salon)
):
    """Возвращает карточку салона текущего владельца."""
    return salon


@router.put("/my-salon", response_model=SalonResponse)
async def update_my_salon(
    update_data: SalonUpdateRequest,
    salon: Salon = Depends(get_owner_salon),
    db: AsyncSession = Depends(get_db)
):
    """Обновляет информацию о своём салоне."""
    if update_data.name is not None:
        salon.name = update_data.name
    if update_data.description is not None:
        salon.description = update_data.description
    if update_data.phone is not None:
        salon.phone = update_data.phone
    if update_data.address is not None:
        salon.address = update_data.address
    if update_data.working_hours is not None:
        salon.working_hours = update_data.working_hours
    
    if update_data.photos is not None:
        old_photos = await db.execute(
            select(SalonPhoto).where(SalonPhoto.salon_id == salon.id)
        )
        for photo in old_photos.scalars().all():
            await db.delete(photo)
        
        for url in update_data.photos:
            new_photo = SalonPhoto(salon_id=salon.id, url=url)
            db.add(new_photo)
    
    await db.commit()
    await db.refresh(salon)
    return salon


@router.get("/my-salon/masters", response_model=List[MasterResponse])
async def get_my_masters(
    salon: Salon = Depends(get_owner_salon),
    db: AsyncSession = Depends(get_db)
):
    """Список всех мастеров моего салона."""
    result = await db.execute(
        select(Master).where(Master.salon_id == salon.id)
    )
    return result.scalars().all()


@router.get("/my-salon/promotions", response_model=List[PromotionResponse])
async def get_my_promotions(
    salon: Salon = Depends(get_owner_salon),
    db: AsyncSession = Depends(get_db)
):
    """Список акций моего салона."""
    result = await db.execute(
        select(Promotion).where(Promotion.salon_id == salon.id)
    )
    return result.scalars().all()


@router.post("/my-salon/promotions", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
async def create_promotion(
    promotion_data: PromotionResponse,
    salon: Salon = Depends(get_owner_salon),
    db: AsyncSession = Depends(get_db)
):
    """Создаёт новую акцию для салона."""
    new_promotion = Promotion(
        salon_id=salon.id,
        title=promotion_data.title,
        description=promotion_data.description,
        tag=promotion_data.tag
    )
    db.add(new_promotion)
    await db.commit()
    await db.refresh(new_promotion)
    return new_promotion


@router.get("/my-salon/dashboard")
async def get_business_dashboard(
    salon: Salon = Depends(get_owner_salon),
    db: AsyncSession = Depends(get_db)
):
    """Возвращает сводку для панели бизнеса."""
    from app.models.models import Booking, BookingStatus
    from sqlalchemy import func as sql_func
    from datetime import datetime, timedelta
    
    masters_count = len(salon.masters)
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    bookings_today = await db.execute(
        select(sql_func.count(Booking.id)).where(
            Booking.master_id.in_([m.id for m in salon.masters]),
            Booking.start_time >= today_start,
            Booking.start_time < today_end
        )
    )
    today_count = bookings_today.scalar() or 0
    
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    revenue_month = await db.execute(
        select(sql_func.sum(Booking.final_price)).where(
            Booking.master_id.in_([m.id for m in salon.masters]),
            Booking.start_time >= month_start,
            Booking.status == BookingStatus.COMPLETED
        )
    )
    revenue = revenue_month.scalar() or 0
    
    return {
        "salon_name": salon.name,
        "masters_count": masters_count,
        "today_bookings": today_count,
        "monthly_revenue": revenue,
        "rating": salon.rating,
        "reviews_count": salon.reviews_count
    }