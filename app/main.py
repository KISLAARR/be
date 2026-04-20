# app/main.py
from geopy.distance import geodesic
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.models.models import Salon, Master, User, Service
from app.schemas.salon import SalonResponse, SalonWithDistance
from app.schemas.master import MasterResponse, ServiceResponse

app = FastAPI(
    title="Beauty Platform API",
    description="API для платформы красоты Руми",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Руми API!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/v1/salons", response_model=List[SalonResponse])
async def get_salons(db: AsyncSession = Depends(get_db)):
    """Получить список всех салонов"""
    result = await db.execute(select(Salon).where(Salon.is_active == True))
    salons = result.scalars().all()
    return salons

@app.get("/api/v1/salons/nearby", response_model=List[SalonWithDistance])
async def get_nearby_salons(
    lat: float,
    lon: float,
    radius: float = 5.0,
    db: AsyncSession = Depends(get_db)
):
    """Получить салоны в радиусе N километров от указанных координат"""
    
    result = await db.execute(select(Salon).where(Salon.is_active == True))
    salons = result.scalars().all()
    
    user_location = (lat, lon)
    nearby_salons = []
    
    for salon in salons:
        salon_location = (salon.latitude, salon.longitude)
        distance = geodesic(user_location, salon_location).kilometers
        
        if distance <= radius:
            salon.distance_km = round(distance, 2)
            nearby_salons.append(salon)
    
    nearby_salons.sort(key=lambda s: s.distance_km)
    return nearby_salons

@app.get("/api/v1/salons/{salon_id}", response_model=SalonResponse)
async def get_salon(salon_id: int, db: AsyncSession = Depends(get_db)):
    """Получить информацию о конкретном салоне"""
    result = await db.execute(select(Salon).where(Salon.id == salon_id))
    salon = result.scalar_one_or_none()
    if not salon:
        raise HTTPException(status_code=404, detail="Салон не найден")
    return salon

@app.get("/api/v1/masters", response_model=List[MasterResponse])
async def get_masters(db: AsyncSession = Depends(get_db)):
    """Получить список всех мастеров"""
    result = await db.execute(
        select(Master)
        .where(Master.is_active == True)
        .order_by(Master.rating.desc())
    )
    masters = result.scalars().all()
    
    for master in masters:
        user_result = await db.execute(select(User).where(User.id == master.user_id))
        master.user = user_result.scalar_one_or_none()
        
        services_result = await db.execute(
            select(Service).where(Service.master_id == master.id)
        )
        master.services = services_result.scalars().all()
    
    return masters

@app.get("/api/v1/masters/{master_id}", response_model=MasterResponse)
async def get_master(master_id: int, db: AsyncSession = Depends(get_db)):
    """Получить информацию о конкретном мастере"""
    result = await db.execute(select(Master).where(Master.id == master_id))
    master = result.scalar_one_or_none()
    if not master:
        raise HTTPException(status_code=404, detail="Мастер не найден")
    
    user_result = await db.execute(select(User).where(User.id == master.user_id))
    master.user = user_result.scalar_one_or_none()
    
    services_result = await db.execute(
        select(Service).where(Service.master_id == master.id)
    )
    master.services = services_result.scalars().all()
    
    return master