# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.db.session import get_db
from app.models.models import User, UserRole
from app.core.config import settings

router = APIRouter()

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(user_id: int) -> str:
    """Создаёт JWT-токен для пользователя."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "exp": expire
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль."""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Хеширует пароль."""
    return pwd_context.hash(password)


@router.post("/auth/register")
async def register(
    phone: str,
    password: str,
    full_name: str = None,
    role: UserRole = UserRole.CLIENT,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    phone — в формате +7XXXXXXXXXX
    password — любой
    role — client / model / business
    """
    # Проверяем, не занят ли телефон
    existing = await db.execute(select(User).where(User.phone == phone))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким номером уже зарегистрирован"
        )
    
    user = User(
        phone=phone,
        full_name=full_name,
        hashed_password=hash_password(password),
        role=role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    token = create_access_token(user.id)
    
    return {
        "user": {
            "id": user.id,
            "phone": user.phone,
            "full_name": user.full_name,
            "role": user.role
        },
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/auth/login")
async def login(
    phone: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход в систему.
    Возвращает JWT-токен, который нужно передавать в заголовке Authorization: Bearer <токен>
    """
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный номер телефона или пароль"
        )
    
    token = create_access_token(user.id)
    
    return {
        "user": {
            "id": user.id,
            "phone": user.phone,
            "full_name": user.full_name,
            "role": user.role
        },
        "access_token": token,
        "token_type": "bearer"
    }