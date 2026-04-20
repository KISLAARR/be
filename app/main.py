# app/main.py
from fastapi import FastAPI

# Создаем экземпляр приложения
app = FastAPI(
    title="Beauty Platform",
    description="API для платформы красоты",
    version="0.1.0"
)

# Самый простой эндпоинт для проверки жизни сервера
@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Руми API! Всё работает отлично."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}