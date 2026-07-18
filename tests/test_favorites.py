# tests/test_favorites.py
"""Избранное: toggle без дублей, уникальный индекс, самоизлечение."""
import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.models import Favorite, Salon
from tests.conftest import register_user

PHONE = "+79992223355"


async def _make_salon(db_session) -> int:
    async with db_session() as db:
        salon = Salon(name="Изб", address="а", phone="+70000000003",
                      latitude=1.0, longitude=1.0, timezone="Europe/Moscow")
        db.add(salon)
        await db.commit()
        await db.refresh(salon)
        return salon.id


async def _login_web(client: httpx.AsyncClient, phone: str) -> None:
    """Cookie-сессия: toggle-эндпоинты аутентифицируются по cookie."""
    r = await client.post(
        "/api/v1/auth/login-web",
        data={"phone": phone, "password": "Testpass1"},
    )
    assert r.status_code == 302


async def test_toggle_adds_then_removes(client, db_session):
    salon_id = await _make_salon(db_session)
    data = await register_user(client, PHONE)
    await _login_web(client, PHONE)

    r = await client.post(f"/api/v1/favorites/toggle-salon/{salon_id}")
    assert r.status_code == 302 and "added=1" in r.headers["location"]

    async with db_session() as db:
        rows = (await db.execute(select(Favorite))).scalars().all()
        assert len(rows) == 1

    r = await client.post(f"/api/v1/favorites/toggle-salon/{salon_id}")
    assert r.status_code == 302 and "removed=1" in r.headers["location"]

    async with db_session() as db:
        rows = (await db.execute(select(Favorite))).scalars().all()
        assert rows == []


async def test_unique_index_blocks_duplicates(db_session):
    """Гонка двух параллельных добавлений: вторую строку не пускает БД."""
    salon_id = await _make_salon(db_session)
    async with db_session() as db:
        from app.models.models import User, UserRole
        user = User(phone="+79992223356", hashed_password="x", role=UserRole.CLIENT)
        db.add(user)
        await db.flush()
        db.add(Favorite(user_id=user.id, salon_id=salon_id))
        await db.commit()
        db.add(Favorite(user_id=user.id, salon_id=salon_id))
        with pytest.raises(IntegrityError):
            await db.commit()


async def test_toggle_heals_historical_duplicates(client, db_session, monkeypatch):
    """Старые дубли (до уникального индекса) удаляются одним toggle, не 500."""
    salon_id = await _make_salon(db_session)
    data = await register_user(client, PHONE)
    user_id = data["user"]["id"]
    await _login_web(client, PHONE)

    from sqlalchemy import text

    # Эмулируем исторические дубли: временно снимаем индекс (как было до
    # миграции), вставляем пару одинаковых строк
    async with db_session() as db:
        await db.execute(text("DROP INDEX uq_favorite_user_salon"))
        await db.commit()
    async with db_session() as db:
        db.add(Favorite(user_id=user_id, salon_id=salon_id))
        db.add(Favorite(user_id=user_id, salon_id=salon_id))
        await db.commit()

    # Раньше здесь был 500 (MultipleResultsFound); теперь — удаление всех дублей
    r = await client.post(f"/api/v1/favorites/toggle-salon/{salon_id}")
    assert r.status_code == 302 and "removed=1" in r.headers["location"]

    async with db_session() as db:
        rows = (await db.execute(select(Favorite))).scalars().all()
        assert rows == []
        await db.execute(text(
            "CREATE UNIQUE INDEX uq_favorite_user_salon ON favorites (user_id, salon_id) "
            "WHERE salon_id IS NOT NULL"
        ))
        await db.commit()
