# app/api/v1/endpoints/reviews.py
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.review_service import ReviewService, ReviewError


router = APIRouter()


@router.post("/reviews/create")
async def create_review_web(
    request: Request,
    master_id: int = Form(...),
    salon_id: int = Form(...),
    rating: int = Form(...),
    comment: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Создание отзыва. Вся проверка прав/состояния — в ReviewService."""
    from app.web.auth import get_current_user_from_cookie

    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        await ReviewService.create_review(
            db,
            client_id=user.id,
            master_id=master_id,
            salon_id=salon_id,
            rating=rating,
            comment=comment,
        )
    except ReviewError as e:
        return HTMLResponse(content=f"<h1>{e.message}</h1>", status_code=e.status)

    return RedirectResponse(url=f"/salons/{salon_id}?reviewed=1", status_code=302)

