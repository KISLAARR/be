# app/api/v1/endpoints/reviews.py
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.models import Review, Salon, Master

router = APIRouter()


@router.post("/reviews/create")
async def create_review_web(
    request: Request,
    master_id: int = Form(...),
    salon_id: int = Form(...),
    rating: int = Form(...),
    comment: str = Form(""),
    db: AsyncSession = Depends(get_db)
):
    """Создание отзыва с пересчётом рейтинга."""
    from app.web.auth import get_current_user_from_cookie
    
    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Проверяем, что оценка от 1 до 5
    if rating < 1 or rating > 5:
        return HTMLResponse(content="<h1>Оценка должна быть от 1 до 5</h1>", status_code=400)
    
    # Создаём отзыв
    review = Review(
        client_id=user.id,
        master_id=master_id,
        salon_id=salon_id,
        rating=rating,
        comment=comment
    )
    db.add(review)
    
    # Пересчитываем рейтинг мастера
    master = (await db.execute(select(Master).where(Master.id == master_id))).scalar_one_or_none()
    if master:
        avg_result = await db.execute(
            select(func.avg(Review.rating)).where(Review.master_id == master_id)
        )
        new_rating = avg_result.scalar() or 0.0
        master.rating = round(float(new_rating), 1)
    
    # Пересчитываем рейтинг салона
    salon = (await db.execute(select(Salon).where(Salon.id == salon_id))).scalar_one_or_none()
    if salon:
        salon.reviews_count = (salon.reviews_count or 0) + 1
        avg_result = await db.execute(
            select(func.avg(Review.rating)).where(Review.salon_id == salon_id)
        )
        new_rating = avg_result.scalar() or 0.0
        salon.rating = round(float(new_rating), 1)
    
    await db.commit()
    
    return RedirectResponse(url=f"/salons/{salon_id}?reviewed=1", status_code=302)