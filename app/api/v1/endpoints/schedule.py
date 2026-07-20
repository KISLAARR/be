# app/api/v1/endpoints/schedule.py
"""Закрытие календарных дат для записи (весь салон или один мастер)."""
from datetime import date as date_type
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import User
from app.api.deps import get_current_user, check_salon_permission
from app.services.schedule_service import ScheduleService, ScheduleError

router = APIRouter()


@router.get("/salon/{salon_id}/closures")
async def list_closures(
    salon_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_salon_permission(db, current_user, salon_id, "manage_schedule")
    closures = await ScheduleService.list_closures(db, salon_id)
    return [
        {
            "id": c.id, "date": c.date.isoformat(), "master_id": c.master_id,
            "reason": c.reason, "created_at": c.created_at.isoformat(),
        }
        for c in closures
    ]


class CloseDateRequest(BaseModel):
    date: date_type
    master_id: Optional[int] = None
    reason: Optional[str] = None


@router.post("/salon/{salon_id}/closures", status_code=status.HTTP_201_CREATED)
async def create_closure(
    salon_id: int,
    body: CloseDateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_salon_permission(db, current_user, salon_id, "manage_schedule")
    try:
        closure = await ScheduleService.close_date(
            db, salon_id=salon_id, master_id=body.master_id, date=body.date,
            reason=body.reason, actor=current_user,
        )
    except ScheduleError as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    return {"id": closure.id, "date": closure.date.isoformat(), "master_id": closure.master_id}


@router.delete("/salon/{salon_id}/closures/{closure_id}")
async def delete_closure(
    salon_id: int,
    closure_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_salon_permission(db, current_user, salon_id, "manage_schedule")
    try:
        await ScheduleService.reopen_date(db, closure_id=closure_id, salon_id=salon_id)
    except ScheduleError as e:
        raise HTTPException(status_code=e.status, detail=e.message)
    return {"status": "reopened"}
