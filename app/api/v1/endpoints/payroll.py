# app/api/v1/endpoints/payroll.py
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Master, User
from app.api.deps import check_salon_permission, get_current_user
from app.services.payroll_service import PayrollService, PayrollError

router = APIRouter()


async def _master_or_404(db: AsyncSession, master_id: int) -> Master:
    master = (await db.execute(select(Master).where(Master.id == master_id))).scalar_one_or_none()
    if not master:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Мастер не найден")
    return master


def _parse_period(period: Optional[str]) -> datetime:
    if not period:
        return datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    try:
        return datetime.strptime(period, "%Y-%m")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Формат периода: YYYY-MM")


@router.get("/master/{master_id}")
async def get_master_payroll(
    master_id: int,
    period: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Расчёт зарплаты мастера за месяц (по умолчанию — текущий)."""
    master = await _master_or_404(db, master_id)
    await check_salon_permission(db, current_user, master.salon_id, "manage_payroll")

    result = await PayrollService.calculate_payroll(db, master_id=master_id, period_month=_parse_period(period))
    return {
        "master_id": result["master_id"],
        "period_month": result["period_month"].strftime("%Y-%m"),
        "revenue": result["revenue"],
        "base_salary": result["base_salary"],
        "commission_percent": result["commission_percent"],
        "commission": result["commission"],
        "adjustments_sum": result["adjustments_sum"],
        "total": result["total"],
        "adjustments": [
            {"id": a.id, "amount": a.amount, "reason": a.reason, "created_at": a.created_at.isoformat()}
            for a in result["adjustments"]
        ],
    }


@router.post("/master/{master_id}/settings")
async def update_payroll_settings_web(
    master_id: int,
    request: Request,
    base_salary: int = Form(...),
    commission_percent: float = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Задаёт ставку мастера: оклад за период + % от выручки."""
    from app.web.auth import get_current_user_from_cookie

    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    master = await _master_or_404(db, master_id)
    try:
        await check_salon_permission(db, user, master.salon_id, "manage_payroll")
    except HTTPException:
        return HTMLResponse(content="Недостаточно прав для управления зарплатами", status_code=403)

    try:
        await PayrollService.set_settings(db, master_id=master_id, base_salary=base_salary, commission_percent=commission_percent)
    except PayrollError as e:
        return HTMLResponse(content=e.message, status_code=e.status)

    return RedirectResponse(url="/business/dashboard?tab=payroll&settings_saved=1", status_code=302)


@router.post("/master/{master_id}/adjustment")
async def add_payroll_adjustment_web(
    master_id: int,
    request: Request,
    amount: int = Form(...),
    reason: str = Form(...),
    period_month: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Ручное начисление бонуса (amount > 0) или штрафа (amount < 0) мастеру."""
    from app.web.auth import get_current_user_from_cookie

    user = await get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    master = await _master_or_404(db, master_id)
    try:
        await check_salon_permission(db, user, master.salon_id, "manage_payroll")
    except HTTPException:
        return HTMLResponse(content="Недостаточно прав для управления зарплатами", status_code=403)

    try:
        period = datetime.strptime(period_month, "%Y-%m")
    except ValueError:
        return HTMLResponse(content="Некорректный период", status_code=400)

    try:
        await PayrollService.add_adjustment(
            db, master_id=master_id, amount=amount, reason=reason, period_month=period, actor=user,
        )
    except PayrollError as e:
        return HTMLResponse(content=e.message, status_code=e.status)

    return RedirectResponse(url="/business/dashboard?tab=payroll&adjustment_added=1", status_code=302)
