# clean_db.py
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.models import Promotion, Service, Master, Salon

async def clean():
    async with AsyncSessionLocal() as s:
        await s.execute(Promotion.__table__.delete())
        await s.execute(Service.__table__.delete())
        await s.execute(Master.__table__.delete())
        await s.execute(Salon.__table__.delete())
        await s.commit()
        print("✅ Старые данные удалены")

asyncio.run(clean())