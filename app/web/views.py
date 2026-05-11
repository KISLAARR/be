# app/web/views.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta, timezone, date as date_type

from app.db.session import get_db
from app.models.models import Salon, Master, User, Service, Promotion, Booking, BookingStatus
from app.core.security import decode_access_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Московский часовой пояс (UTC+3)
MSK = timezone(timedelta(hours=3))

def get_current_user_from_cookie(request: Request) -> User | None:
    """Пытаемся получить пользователя из токена в заголовке или куках (для веб-страниц)"""
    return None

@router.get("/")
async def index(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/salons")
async def salons_list(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница со списком салонов"""
    result = await db.execute(
        select(Salon)
        .where(Salon.is_active == True)
        .order_by(Salon.rating.desc())
    )
    salons = result.scalars().all()
    
    return templates.TemplateResponse(
        "salons/list.html",
        {"request": request, "salons": salons}
    )

@router.get("/salons/{salon_id}")
async def salon_detail(request: Request, salon_id: int, db: AsyncSession = Depends(get_db)):
    """Страница конкретного салона"""
    result = await db.execute(select(Salon).where(Salon.id == salon_id))
    salon = result.scalar_one_or_none()
    
    if not salon:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    masters_result = await db.execute(
        select(Master)
        .where(Master.salon_id == salon_id, Master.is_active == True)
        .options(selectinload(Master.user), selectinload(Master.services))
    )
    masters = masters_result.scalars().all()
    
    promos_result = await db.execute(
        select(Promotion).where(Promotion.salon_id == salon_id, Promotion.is_active == True)
    )
    promotions = promos_result.scalars().all()
    
    return templates.TemplateResponse(
        "salons/detail.html",
        {
            "request": request,
            "salon": salon,
            "masters": masters,
            "promotions": promotions
        }
    )

@router.get("/profile")
async def profile(request: Request):
    """Страница профиля пользователя"""
    return templates.TemplateResponse(
        "profile/index.html",
        {"request": request}
    )

@router.get("/model")
async def model_plans(request: Request):
    """Страница подписки модели"""
    return templates.TemplateResponse(
        "model/plans.html",
        {"request": request}
    )

@router.get("/business")
async def business(request: Request):
    """Страница для бизнеса"""
    return templates.TemplateResponse(
        "business/index.html",
        {"request": request}
    )

@router.get("/bookings")
async def bookings_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Страница 'Мои записи' — показывает записи с московским временем"""
    
    user_id = request.query_params.get("user_id")
    
    if user_id:
        result = await db.execute(
            select(Booking)
            .where(Booking.client_id == int(user_id))
            .order_by(Booking.start_time.asc())
            .options(
                selectinload(Booking.master).selectinload(Master.user),
                selectinload(Booking.master).selectinload(Master.salon),
                selectinload(Booking.service)
            )
        )
    else:
        result = await db.execute(
            select(Booking)
            .order_by(Booking.start_time.asc())
            .options(
                selectinload(Booking.master).selectinload(Master.user),
                selectinload(Booking.master).selectinload(Master.salon),
                selectinload(Booking.service)
            )
        )
    
    bookings = result.scalars().all()
    
    # Переводим время из UTC в MSK для отображения
    for b in bookings:
        if b.start_time and b.start_time.tzinfo is None:
            b.start_time = b.start_time.replace(tzinfo=timezone.utc)
        if b.end_time and b.end_time.tzinfo is None:
            b.end_time = b.end_time.replace(tzinfo=timezone.utc)
        if b.start_time and b.start_time.tzinfo:
            b.start_time = b.start_time.astimezone(MSK)
        if b.end_time and b.end_time.tzinfo:
            b.end_time = b.end_time.astimezone(MSK)
    
    return templates.TemplateResponse(
        "bookings/index.html",
        {
            "request": request,
            "bookings": bookings,
            "today_date": date_type.today(),
            "timedelta": timedelta
        }
    )

@router.get("/favorites")
async def favorites_page(request: Request):
    """Страница 'Избранное'"""
    return templates.TemplateResponse(
        "favorites/index.html", 
        {"request": request}
    )

@router.get("/settings")
async def settings_page(request: Request):
    """Страница 'Настройки'"""
    return templates.TemplateResponse(
        "settings/index.html", 
        {"request": request}
    )

# ========== АВТОРИЗАЦИЯ ==========

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

# ========== БРОНИРОВАНИЕ ==========

@router.get("/book/{master_id}")
async def book_service(request: Request, master_id: int, db: AsyncSession = Depends(get_db)):
    """Выбор услуги мастера"""
    result = await db.execute(
        select(Master)
        .where(Master.id == master_id, Master.is_active == True)
        .options(selectinload(Master.user), selectinload(Master.services))
    )
    master = result.scalar_one_or_none()
    
    if not master:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    salon_result = await db.execute(select(Salon).where(Salon.id == master.salon_id))
    salon = salon_result.scalar_one()
    
    return templates.TemplateResponse(
        "booking/service.html",
        {"request": request, "master": master, "salon": salon}
    )

@router.get("/book/{master_id}/service/{service_id}")
async def book_datetime(request: Request, master_id: int, service_id: int, db: AsyncSession = Depends(get_db)):
    """Выбор даты и времени"""
    master_result = await db.execute(
        select(Master).where(Master.id == master_id).options(selectinload(Master.user))
    )
    master = master_result.scalar_one_or_none()
    if not master:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    service_result = await db.execute(select(Service).where(Service.id == service_id))
    service = service_result.scalar_one_or_none()
    if not service:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    salon_result = await db.execute(select(Salon).where(Salon.id == master.salon_id))
    salon = salon_result.scalar_one()
    
    return templates.TemplateResponse(
        "booking/datetime.html",
        {"request": request, "master": master, "service": service, "salon": salon}
    )

@router.get("/book/{master_id}/service/{service_id}/confirm")
async def book_confirm_get(request: Request, master_id: int, service_id: int, date: str = "", time: str = "", db: AsyncSession = Depends(get_db)):
    """Страница подтверждения"""
    master_result = await db.execute(
        select(Master).where(Master.id == master_id).options(selectinload(Master.user))
    )
    master = master_result.scalar_one_or_none()
    if not master:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    service_result = await db.execute(select(Service).where(Service.id == service_id))
    service = service_result.scalar_one_or_none()
    if not service:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    salon_result = await db.execute(select(Salon).where(Salon.id == master.salon_id))
    salon = salon_result.scalar_one()
    
    return templates.TemplateResponse(
        "booking/confirm.html",
        {
            "request": request,
            "master": master,
            "service": service,
            "salon": salon,
            "date": date,
            "time": time,
            "success": False
        }
    )

@router.get("/master/schedule")
async def master_schedule_page(request: Request):
    """Страница расписания мастера"""
    return templates.TemplateResponse(
        "master/schedule.html",
        {"request": request}
    )