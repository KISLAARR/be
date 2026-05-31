# app/web/auth.py
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from app.db.session import get_db
from app.models.models import User
from app.core.config import settings


async def get_current_user_from_cookie(request: Request, db: AsyncSession = Depends(get_db)):
    """Получает текущего пользователя из JWT-токена в куках."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    return user