# app/web/auth.py
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.models import User
from app.core.security import decode_access_token


async def get_current_user_from_cookie(request: Request, db: AsyncSession = Depends(get_db)):
    """Получает текущего пользователя из JWT-токена в куках."""
    token = request.cookies.get("access_token")
    if not token:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    return user
