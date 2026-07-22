# tests/test_soft_deletes.py
"""Мягкое удаление услуги и салона владельцем: без 500 на FK, история цела,
объект исчезает из выбора/записи."""
from datetime import datetime, timedelta

from sqlalchemy import select

from app.core.security import get_password_hash
from app.models.models import (
    User, UserRole, Salon, SalonMember, SalonRole, Master, Service,
    Booking, BookingStatus,
)


async def _login(client, phone, password="Testpass1"):
    r = await client.post("/api/v1/auth/login", json={"phone": phone, "password": password})
    client.cookies.set("access_token", r.json()["access_token"])


async def _salon_owner_master_service(db_session, *, owner_phone, salon_phone):
    """Салон + владелец (manage_masters+manage_salon, is_creator) + мастер + услуга."""
    async with db_session() as db:
        salon = Salon(name="S", address="a", phone=salon_phone,
                      latitude=1.0, longitude=1.0, timezone="Europe/Moscow")
        db.add(salon)
        await db.commit()
        await db.refresh(salon)
        owner = User(phone=owner_phone, full_name="Owner",
                     hashed_password=get_password_hash("Testpass1"), role=UserRole.BUSINESS)
        muser = User(phone=salon_phone[:-1] + "1", full_name="M",
                     hashed_password=get_password_hash("Testpass1"), role=UserRole.CLIENT)
        db.add_all([owner, muser])
        await db.commit()
        await db.refresh(owner)
        await db.refresh(muser)
        salon.creator_id = owner.id
        db.add(SalonMember(salon_id=salon.id, user_id=owner.id, role=SalonRole.OWNER,
                           is_creator=True,
                           permissions={"manage_masters": True, "manage_salon": True},
                           is_active=True))
        master = Master(salon_id=salon.id, user_id=muser.id, specialization="Барбер")
        db.add(master)
        await db.commit()
        await db.refresh(master)
        svc = Service(master_id=master.id, name="Стрижка", price=1000, duration_minutes=60)
        db.add(svc)
        await db.commit()
        await db.refresh(svc)
        return salon.id, master.id, svc.id


async def test_delete_service_with_booking_soft(client, db_session):
    """Раньше 500 (Booking.service_id NOT NULL). Теперь soft-delete."""
    salon_id, master_id, svc_id = await _salon_owner_master_service(
        db_session, owner_phone="+79993330080", salon_phone="+70000000080")
    # бронь к этой услуге (это и роняло hard-delete)
    async with db_session() as db:
        cu = User(phone="+79993330082", full_name="C",
                  hashed_password=get_password_hash("Testpass1"), role=UserRole.CLIENT)
        db.add(cu)
        await db.commit()
        await db.refresh(cu)
        start = datetime.now() + timedelta(days=1)
        db.add(Booking(client_id=cu.id, master_id=master_id, service_id=svc_id,
                       start_time=start, end_time=start + timedelta(minutes=60),
                       status=BookingStatus.PENDING, final_price=1000))
        await db.commit()

    await _login(client, "+79993330080")
    r = await client.post(f"/api/v1/services/{svc_id}/delete")
    assert r.status_code == 302 and "deleted=1" in r.headers["location"], r.headers.get("location")

    async with db_session() as db:
        svc = (await db.execute(select(Service).where(Service.id == svc_id))).scalar_one()
        assert svc.is_active is False  # скрыта, не удалена
        # бронь (история) цела
        assert (await db.execute(select(Booking).where(Booking.service_id == svc_id))).scalar_one_or_none() is not None
        # из выбора/записи ушла: booking-путь (Service.id ∧ is_active) не находит
        assert (await db.execute(
            select(Service).where(Service.id == svc_id, Service.is_active == True)
        )).scalar_one_or_none() is None


async def test_owner_delete_salon_soft(client, db_session):
    """Владелец «удаляет» салон → soft-delete (is_active=False), данные целы, без 500."""
    salon_id, master_id, svc_id = await _salon_owner_master_service(
        db_session, owner_phone="+79993330085", salon_phone="+70000000085")

    await _login(client, "+79993330085")
    r = await client.request("DELETE", f"/api/v1/business/my-salon?salon_id={salon_id}")
    assert r.status_code == 200, r.text
    assert r.json().get("status") == "deleted"

    async with db_session() as db:
        salon = (await db.execute(select(Salon).where(Salon.id == salon_id))).scalar_one()
        assert salon.is_active is False  # скрыт, не удалён
        # мастер и услуга целы
        assert (await db.execute(select(Master).where(Master.id == master_id))).scalar_one_or_none() is not None
        assert (await db.execute(select(Service).where(Service.id == svc_id))).scalar_one_or_none() is not None
