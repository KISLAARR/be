# app/api/v1/endpoints/loyalty.py
"""Лояльность салона: настройки, именные скидки/промокоды, статус и баллы клиента."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import User, SalonLoyaltySettings, LoyaltyOffer
from app.api.deps import get_current_user, check_salon_permission
from app.services.loyalty_service import LoyaltyService, LoyaltyError

router = APIRouter()


# ========== Настройки программы лояльности салона ==========

@router.get("/salon/{salon_id}/settings")
async def get_loyalty_settings(
    salon_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Настройки лояльности салона (0/дефолты, если ещё не заданы)."""
    await check_salon_permission(db, current_user, salon_id, "manage_salon")
    settings = (await db.execute(
        select(SalonLoyaltySettings).where(SalonLoyaltySettings.salon_id == salon_id)
    )).scalar_one_or_none()
    return {
        "regular_client_discount_percent": settings.regular_client_discount_percent if settings else 0,
        "regular_client_visits_threshold": settings.regular_client_visits_threshold if settings else None,
        "bonus_accrual_percent": settings.bonus_accrual_percent if settings else 0,
    }


class LoyaltySettingsRequest(BaseModel):
    regular_client_discount_percent: int = 0
    regular_client_visits_threshold: Optional[int] = None
    bonus_accrual_percent: float = 0


@router.put("/salon/{salon_id}/settings")
async def update_loyalty_settings(
    salon_id: int,
    body: LoyaltySettingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создаёт/обновляет настройки лояльности салона."""
    await check_salon_permission(db, current_user, salon_id, "manage_salon")
    if not (0 <= body.regular_client_discount_percent < 100):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Скидка постоянного клиента должна быть от 0 до 99%")
    if not (0 <= body.bonus_accrual_percent < 100):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="% автоначисления баллов должен быть от 0 до 99")

    settings = (await db.execute(
        select(SalonLoyaltySettings).where(SalonLoyaltySettings.salon_id == salon_id)
    )).scalar_one_or_none()
    if settings is None:
        settings = SalonLoyaltySettings(salon_id=salon_id)
        db.add(settings)
    settings.regular_client_discount_percent = body.regular_client_discount_percent
    settings.regular_client_visits_threshold = body.regular_client_visits_threshold
    settings.bonus_accrual_percent = body.bonus_accrual_percent
    await db.commit()
    return {"status": "ok"}


# ========== Именные скидки / промокоды («позиции») ==========

@router.get("/salon/{salon_id}/offers")
async def list_loyalty_offers(
    salon_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_salon_permission(db, current_user, salon_id, "manage_salon")
    result = await db.execute(
        select(LoyaltyOffer).where(LoyaltyOffer.salon_id == salon_id).order_by(LoyaltyOffer.created_at.desc())
    )
    return [
        {"id": o.id, "title": o.title, "discount_percent": o.discount_percent,
         "promo_code": o.promo_code, "is_active": o.is_active}
        for o in result.scalars().all()
    ]


class LoyaltyOfferRequest(BaseModel):
    title: str
    discount_percent: int
    promo_code: Optional[str] = None


@router.post("/salon/{salon_id}/offers", status_code=status.HTTP_201_CREATED)
async def create_loyalty_offer(
    salon_id: int,
    body: LoyaltyOfferRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_salon_permission(db, current_user, salon_id, "manage_salon")
    if not body.title.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите название скидки")
    if not (0 < body.discount_percent < 100):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Скидка должна быть от 1 до 99%")

    promo_code = body.promo_code.strip() or None if body.promo_code else None
    if promo_code:
        existing = (await db.execute(
            select(LoyaltyOffer).where(LoyaltyOffer.salon_id == salon_id, LoyaltyOffer.promo_code == promo_code)
        )).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Такой промокод уже есть в этом салоне")

    offer = LoyaltyOffer(salon_id=salon_id, title=body.title.strip(), discount_percent=body.discount_percent, promo_code=promo_code)
    db.add(offer)
    await db.commit()
    await db.refresh(offer)
    return {"id": offer.id, "title": offer.title, "discount_percent": offer.discount_percent, "promo_code": offer.promo_code}


@router.delete("/salon/{salon_id}/offers/{offer_id}")
async def delete_loyalty_offer(
    salon_id: int,
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_salon_permission(db, current_user, salon_id, "manage_salon")
    offer = (await db.execute(
        select(LoyaltyOffer).where(LoyaltyOffer.id == offer_id, LoyaltyOffer.salon_id == salon_id)
    )).scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Скидка не найдена")
    await db.delete(offer)
    await db.commit()
    return {"status": "deleted"}


# ========== Статус и баллы конкретного клиента ==========

@router.get("/salon/{salon_id}/client/{client_id}")
async def get_client_loyalty_status(
    salon_id: int,
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Сводка для модалки завершения записи: статус, персональная скидка,
    доступные промокоды, баланс баллов. Требует доступа к расписанию —
    именно с этим правом можно завершать записи и выбирать скидку."""
    await check_salon_permission(db, current_user, salon_id, "manage_schedule")
    return await LoyaltyService.get_client_status(db, salon_id, client_id)


class RegularStatusRequest(BaseModel):
    is_regular: bool


@router.post("/salon/{salon_id}/client/{client_id}/status")
async def set_regular_client_status(
    salon_id: int,
    client_id: int,
    body: RegularStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_salon_permission(db, current_user, salon_id, "manage_salon")
    try:
        row = await LoyaltyService.set_regular_client_status(
            db, salon_id=salon_id, client_id=client_id, is_regular=body.is_regular, actor=current_user,
        )
    except LoyaltyError as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    return {"is_regular_client": row.is_regular_client}


class PersonalDiscountRequest(BaseModel):
    discount_percent: Optional[int] = None


@router.post("/salon/{salon_id}/client/{client_id}/personal-discount")
async def set_client_personal_discount(
    salon_id: int,
    client_id: int,
    body: PersonalDiscountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_salon_permission(db, current_user, salon_id, "manage_salon")
    try:
        row = await LoyaltyService.set_personal_discount(
            db, salon_id=salon_id, client_id=client_id, discount_percent=body.discount_percent, actor=current_user,
        )
    except LoyaltyError as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    return {"personal_discount_percent": row.personal_discount_percent}


class PointsAdjustRequest(BaseModel):
    amount: int
    comment: str = ""


@router.post("/salon/{salon_id}/client/{client_id}/points")
async def adjust_client_points(
    salon_id: int,
    client_id: int,
    body: PointsAdjustRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_salon_permission(db, current_user, salon_id, "manage_salon")
    try:
        row = await LoyaltyService.manual_adjust_points(
            db, salon_id=salon_id, client_id=client_id, amount=body.amount, comment=body.comment, actor=current_user,
        )
    except LoyaltyError as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    return {"bonus_points": row.bonus_points}
