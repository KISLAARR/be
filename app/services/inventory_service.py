# app/services/inventory_service.py
"""Складской учёт: мини-склад расходников на каждого мастера.

Единый источник истины — InventoryMovement (журнал движений). Остаток
InventoryItem.quantity денормализован для быстрых выборок и обновляется
только через методы этого сервиса, никогда напрямую.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    InventoryItem, InventoryMovement, InventoryMovementType,
    InventoryAudit, InventoryAuditItem, InventoryAuditStatus,
    Booking, BookingStatus, Master,
)


class InventoryError(Exception):
    """Бизнес-ошибка склада. message — текст для пользователя, status — HTTP-код."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


class InventoryService:
    @staticmethod
    async def get_master_stock(db: AsyncSession, master_id: int) -> list[InventoryItem]:
        """Текущие остатки мини-склада мастера (только активные позиции)."""
        result = await db.execute(
            select(InventoryItem)
            .where(InventoryItem.master_id == master_id, InventoryItem.is_active == True)
            .order_by(InventoryItem.name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def receive_stock(
        db: AsyncSession, *, item_id: int, quantity: float, comment: str, actor,
    ) -> InventoryItem:
        """Приход (закупка): увеличивает остаток позиции."""
        if quantity <= 0:
            raise InventoryError("Количество прихода должно быть положительным")

        item = (await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))).scalar_one_or_none()
        if not item:
            raise InventoryError("Позиция склада не найдена", status=404)

        db.add(InventoryMovement(
            item_id=item.id,
            type=InventoryMovementType.RECEIPT,
            delta=quantity,
            unit_cost_snapshot=item.cost_per_unit,
            created_by_id=actor.id,
            comment=comment or None,
        ))
        item.quantity += quantity
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def log_consumption(
        db: AsyncSession, *, booking_id: int, items: list[dict], actor,
    ) -> Booking:
        """Форма мастера после клиента: списывает фактически потраченные
        расходники по завершённой записи. `items` — [{"item_id": int, "quantity": float}, ...]."""
        if not items:
            raise InventoryError("Укажите хотя бы одну потраченную позицию")

        booking = (await db.execute(select(Booking).where(Booking.id == booking_id))).scalar_one_or_none()
        if not booking:
            raise InventoryError("Запись не найдена", status=404)
        if booking.status != BookingStatus.COMPLETED:
            raise InventoryError("Списать расходники можно только по завершённой записи")
        if booking.consumption_reported:
            raise InventoryError("По этой записи расходники уже списаны", status=409)

        # Валидируем всё до применения — чтобы не списать часть позиций,
        # упершись в нехватку остатка на середине списка.
        resolved: list[tuple[InventoryItem, float]] = []
        for line in items:
            quantity = float(line.get("quantity") or 0)
            if quantity <= 0:
                raise InventoryError("Количество должно быть положительным")
            item = (await db.execute(
                select(InventoryItem).where(InventoryItem.id == line.get("item_id"))
            )).scalar_one_or_none()
            if not item:
                raise InventoryError("Позиция склада не найдена", status=404)
            if item.master_id != booking.master_id:
                raise InventoryError("Позиция склада принадлежит другому мастеру", status=403)
            if item.quantity < quantity:
                raise InventoryError(f"Недостаточно «{item.name}» на складе: остаток {item.quantity} {item.unit}")
            resolved.append((item, quantity))

        for item, quantity in resolved:
            db.add(InventoryMovement(
                item_id=item.id,
                type=InventoryMovementType.CONSUMPTION,
                delta=-quantity,
                unit_cost_snapshot=item.cost_per_unit,
                booking_id=booking.id,
                created_by_id=actor.id,
            ))
            item.quantity -= quantity

        booking.consumption_reported = True
        await db.commit()
        await db.refresh(booking)
        return booking

    @staticmethod
    async def start_audit(db: AsyncSession, *, master_id: int, actor) -> InventoryAudit:
        """Открывает акт инвентаризации: снимает текущие остатки как ожидаемые."""
        open_audit = (await db.execute(
            select(InventoryAudit).where(
                InventoryAudit.master_id == master_id,
                InventoryAudit.status == InventoryAuditStatus.DRAFT,
            )
        )).scalar_one_or_none()
        if open_audit:
            raise InventoryError("У этого мастера уже есть открытый акт инвентаризации", status=409)

        items = await InventoryService.get_master_stock(db, master_id)
        audit = InventoryAudit(master_id=master_id, status=InventoryAuditStatus.DRAFT, created_by_id=actor.id)
        db.add(audit)
        await db.flush()

        for item in items:
            db.add(InventoryAuditItem(audit_id=audit.id, item_id=item.id, expected_quantity=item.quantity))

        await db.commit()
        await db.refresh(audit)
        return audit

    @staticmethod
    async def confirm_audit(
        db: AsyncSession, *, audit_id: int, actual_quantities: dict[int, float], actor,
    ) -> InventoryAudit:
        """Закрывает акт: фиксирует факт, создаёт корректирующие движения по расхождениям."""
        audit = (await db.execute(select(InventoryAudit).where(InventoryAudit.id == audit_id))).scalar_one_or_none()
        if not audit:
            raise InventoryError("Акт инвентаризации не найден", status=404)
        if audit.status != InventoryAuditStatus.DRAFT:
            raise InventoryError("Акт уже закрыт")

        audit_items = (await db.execute(
            select(InventoryAuditItem).where(InventoryAuditItem.audit_id == audit_id)
        )).scalars().all()

        for audit_item in audit_items:
            if audit_item.item_id not in actual_quantities:
                raise InventoryError("Укажите фактический остаток по всем позициям акта")

        for audit_item in audit_items:
            actual = float(actual_quantities[audit_item.item_id])
            audit_item.actual_quantity = actual
            diff = actual - audit_item.expected_quantity
            if diff != 0:
                item = (await db.execute(
                    select(InventoryItem).where(InventoryItem.id == audit_item.item_id)
                )).scalar_one()
                db.add(InventoryMovement(
                    item_id=item.id,
                    type=InventoryMovementType.ADJUSTMENT,
                    delta=diff,
                    unit_cost_snapshot=item.cost_per_unit,
                    created_by_id=actor.id,
                    comment=f"Инвентаризация #{audit.id}",
                ))
                item.quantity = actual

        audit.status = InventoryAuditStatus.CONFIRMED
        audit.confirmed_at = datetime.now()
        await db.commit()
        await db.refresh(audit)
        return audit

    @staticmethod
    async def unreported_bookings(db: AsyncSession, salon_id: int) -> list[Booking]:
        """Завершённые визиты без списания расходников — для напоминания админу."""
        master_ids_result = await db.execute(select(Master.id).where(Master.salon_id == salon_id))
        master_ids = [row[0] for row in master_ids_result.all()]
        if not master_ids:
            return []
        result = await db.execute(
            select(Booking).where(
                Booking.master_id.in_(master_ids),
                Booking.status == BookingStatus.COMPLETED,
                Booking.consumption_reported == False,
            ).order_by(Booking.start_time.desc())
        )
        return list(result.scalars().all())
