# app/web/auth.py
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from app.db.session import get_db
from app.models.models import User, SalonMember
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
    if user is not None:
        # role="business" не всегда синхронизирован с реальным членством в
        # SalonMember (напр. салон подключён владельцу иным путём, без
        # обновления роли) — сайдбару нужен фактический признак доступа
        # к панели бизнеса, а не только устаревшее поле role.
        has_salon = await db.execute(
            select(
                exists().where(
                    SalonMember.user_id == user.id,
                    SalonMember.is_active == True,
                )
            )
        )
        user.has_salon_access = bool(has_salon.scalar())
    return user
