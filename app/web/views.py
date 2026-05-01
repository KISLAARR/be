# app/web/views.py
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.models import Salon, Master, User, Service, Promotion

router = APIRouter()
templates = Jinja2Templates(directory="templates")

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
    # Получаем салон
    result = await db.execute(select(Salon).where(Salon.id == salon_id))
    salon = result.scalar_one_or_none()
    
    if not salon:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    # Получаем мастеров салона вместе с их услугами и данными пользователя
    masters_result = await db.execute(
        select(Master)
        .where(Master.salon_id == salon_id, Master.is_active == True)
        .options(selectinload(Master.user), selectinload(Master.services))
    )
    masters = masters_result.scalars().all()
    
    # Получаем акции салона
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