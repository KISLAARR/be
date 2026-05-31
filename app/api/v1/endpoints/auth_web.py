# app/api/v1/endpoints/auth_web.py
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt
from datetime import datetime, timedelta
import hashlib

from app.db.session import get_db
from app.models.models import User, UserRole
from app.core.config import settings

router = APIRouter()


def create_access_token(user_id: int) -> str:
    """Создаёт JWT-токен."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль (SHA-256 для тестовых, bcrypt для боевых)."""
    # Проверяем через SHA-256 (для тестовых пользователей)
    if hashed_password == hashlib.sha256(plain_password.encode()).hexdigest():
        return True
    # Проверяем через bcrypt (для пользователей из регистрации)
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except:
        return False


@router.post("/auth/login-web")
async def login_web(
    request: Request,
    phone: str = Form(...),
    password: str = Form(...),
    redirect: str = Form("/"),
    db: AsyncSession = Depends(get_db)
):
    """Вход через веб-форму."""
    
    # Ищем пользователя по телефону
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    
    # Проверяем пароль
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse(url=f"/login?error=1&redirect={redirect}", status_code=302)
    
    # Создаём JWT-токен
    token = create_access_token(user.id)
    
    # Создаём ответ с редиректом
    response = RedirectResponse(url=redirect, status_code=302)
    
    # Устанавливаем куку
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,    # JS не может прочитать куку
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",   # Кука работает при переходах между страницами
        path="/"          # Кука доступна на всех страницах сайта
    )
    
    return response


@router.post("/auth/register-web")
async def register_web(
    request: Request,
    phone: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(""),
    role: str = Form("client"),
    db: AsyncSession = Depends(get_db)
):
    """Регистрация через веб-форму."""
    
    # Проверяем, что пользователь не существует
    existing = await db.execute(select(User).where(User.phone == phone))
    if existing.scalar_one_or_none():
        return RedirectResponse(url="/register?error=phone_exists", status_code=302)
    
    # Создаём пользователя
    user_role = UserRole.BUSINESS if role == "business" else UserRole.CLIENT
    
    # Хешируем пароль
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    user = User(
        phone=phone,
        full_name=full_name,
        hashed_password=hashed,
        role=user_role,
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Создаём токен
    token = create_access_token(user.id)
    
    # Перенаправляем в зависимости от роли
    if user_role == UserRole.BUSINESS:
        redirect_url = "/business/dashboard"
    else:
        redirect_url = "/profile"
    
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        path="/"
    )
    return response