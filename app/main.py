# app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.models import Salon, Master, User

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

@app.get("/api/v1/salons")
async def get_salons(db: AsyncSession = Depends(get_db)):
    """Получить список всех салонов"""
    result = await db.execute(select(Salon))
    salons = result.scalars().all()
    return salons

@app.get("/api/v1/salons/{salon_id}")
async def get_salon(salon_id: int, db: AsyncSession = Depends(get_db)):
    """Получить информацию о конкретном салоне"""
    result = await db.execute(select(Salon).where(Salon.id == salon_id))
    salon = result.scalar_one_or_none()
    if not salon:
        return {"error": "Салон не найден"}
    return salon

@app.get("/api/v1/masters")
async def get_masters(db: AsyncSession = Depends(get_db)):
    """Получить список всех мастеров с информацией о них"""
    result = await db.execute(
        select(Master, User)
        .join(User, Master.user_id == User.id)
    )
    masters = []
    for master, user in result:
        masters.append({
            "id": master.id,
            "full_name": user.full_name,
            "specialization": master.specialization,
            "experience_years": master.experience_years,
            "rating": master.rating,
            "photo_url": master.photo_url,
            "salon_id": master.salon_id
        })
    return masters