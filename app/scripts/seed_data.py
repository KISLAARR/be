# app/scripts/seed_data.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.models import Salon, Master, User, Service, Promotion, UserRole, Base 
from app.core.config import settings

async def seed_database():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 1. Создаём салон "Брутальный"
        brutalny = Salon(
            name="Брутальный",
            description="Барбершоп «Брутальный» — место для настоящих мужчин.",
            address="Москва, ул. Тверская, 15",
            latitude=55.761859,
            longitude=37.606138,
            phone="+79991234567",
            rating=4.9,
            reviews_count=156,
            working_hours='{"mon":"10:00-21:00","tue":"10:00-21:00","wed":"10:00-21:00","thu":"10:00-21:00","fri":"10:00-21:00","sat":"11:00-20:00","sun":"11:00-20:00"}'
        )
        session.add(brutalny)
        await session.flush()
        
        # 2. Создаём пользователя-мастера Александра
        user_alex = User(
            phone="+79991112233",
            full_name="Александр Петров",
            hashed_password="hashed_password_placeholder",
            role=UserRole.MASTER,
            is_active=True
        )
        session.add(user_alex)
        await session.flush()
        
        # 3. Создаём мастера Александра
        master_alex = Master(
            user_id=user_alex.id,
            salon_id=brutalny.id,
            specialization="барбер-стилист",
            experience_years=5,
            rating=4.9,
            photo_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face"
        )
        session.add(master_alex)
        await session.flush()
        
        # 4. Добавляем услуги
        services = [
            Service(master_id=master_alex.id, name="Стрижка машинкой", price=1500, duration_minutes=30),
            Service(master_id=master_alex.id, name="Стрижка + борода", price=2400, duration_minutes=60),
            Service(master_id=master_alex.id, name="Моделирование бороды", price=1200, duration_minutes=30),
        ]
        session.add_all(services)
        
        # 5. Добавляем акции
        promotions = [
            Promotion(salon_id=brutalny.id, title="Первый визит −20%", description="Скидка 20% на все услуги для новых клиентов", tag="Новичкам"),
            Promotion(salon_id=brutalny.id, title="Комбо стрижка + борода", description="Стрижка и моделирование бороды за 2200₽ вместо 2400₽", tag="Выгода"),
        ]
        session.add_all(promotions)
        
        await session.commit()
        print("✅ База данных заполнена тестовыми данными!")

if __name__ == "__main__":
    asyncio.run(seed_database())