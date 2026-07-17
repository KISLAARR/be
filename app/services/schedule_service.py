# app/services/schedule_service.py
"""Закрытие конкретных календарных дат для записи — на весь салон или на
одного мастера (отпуск/больничный/праздник/ремонт). Отдельно от
Salon.working_hours (тот описывает только повторяющийся по дням недели
график) — см. app/services/schedule_utils.get_effective_work_hours,
которая объединяет обе вещи при проверке доступности слота.
"""
from __future__ import annotations

from datetime import date as date_type, datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Booking, BookingStatus, Master, ScheduleClosure


class ScheduleError(Exception):
    """Бизнес-ошибка закрытия даты. message — текст для пользователя, status — HTTP-код."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


class ScheduleService:
    @staticmethod
    async def close_date(
        db: AsyncSession, *, salon_id: int, master_id: Optional[int],
        date: date_type, reason: Optional[str], actor,
    ) -> ScheduleClosure:
        """Закрывает дату. master_id=None — весь салон, иначе один мастер.
        Отказывает, если на эту дату (в этом объёме) уже есть активные записи."""
        if master_id is not None:
            master = (await db.execute(select(Master).where(Master.id == master_id))).scalar_one_or_none()
            if master is None or master.salon_id != salon_id:
                raise ScheduleError("Мастер не найден в этом салоне", status=404)
            master_ids = [master_id]
        else:
            master_ids = [
                row[0] for row in (await db.execute(
                    select(Master.id).where(Master.salon_id == salon_id)
                )).all()
            ]

        existing_closure = (await db.execute(
            select(ScheduleClosure).where(
                ScheduleClosure.salon_id == salon_id,
                ScheduleClosure.date == date,
                ScheduleClosure.master_id == master_id,
            )
        )).scalar_one_or_none()
        if existing_closure is not None:
            raise ScheduleError("Эта дата уже закрыта", status=409)

        if master_ids:
            day_start = datetime.combine(date, datetime.min.time())
            day_end = day_start + timedelta(days=1)
            blocking_count = (await db.execute(
                select(Booking.id).where(
                    Booking.master_id.in_(master_ids),
                    Booking.start_time >= day_start,
                    Booking.start_time < day_end,
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                )
            )).all()
            if blocking_count:
                raise ScheduleError(
                    f"Нельзя закрыть дату: на неё уже есть активных записей — {len(blocking_count)}. "
                    "Сначала перенесите или отмените их.",
                    status=409,
                )

        closure = ScheduleClosure(
            salon_id=salon_id, master_id=master_id, date=date,
            reason=(reason or None), created_by_id=actor.id,
        )
        db.add(closure)
        await db.commit()
        await db.refresh(closure)
        return closure

    @staticmethod
    async def reopen_date(db: AsyncSession, *, closure_id: int, salon_id: int) -> None:
        """Удаляет закрытие — день снова открыт для записи."""
        closure = (await db.execute(
            select(ScheduleClosure).where(ScheduleClosure.id == closure_id, ScheduleClosure.salon_id == salon_id)
        )).scalar_one_or_none()
        if closure is None:
            raise ScheduleError("Закрытие не найдено", status=404)
        await db.delete(closure)
        await db.commit()

    @staticmethod
    async def list_closures(db: AsyncSession, salon_id: int, from_date: Optional[date_type] = None) -> list[ScheduleClosure]:
        """Предстоящие закрытия салона (от from_date, по умолчанию — от сегодня)."""
        from_date = from_date or datetime.now().date()
        result = await db.execute(
            select(ScheduleClosure)
            .where(ScheduleClosure.salon_id == salon_id, ScheduleClosure.date >= from_date)
            .order_by(ScheduleClosure.date)
        )
        return list(result.scalars().all())
