"""Уникальность избранного + чистка дублей

Revision ID: e1f2a3b4c5d6
Revises: c9d1e4f7a2b8
Create Date: 2026-07-18

Двойная привязка обработчика на фронте отправляла два параллельных toggle —
оба видели «записи нет» и вставляли по строке. Дубли ломали удаление
(scalar_one_or_none → MultipleResultsFound → 500). Здесь: удаляем дубли
(оставляя самую раннюю строку) и ставим частичные уникальные индексы —
гонка больше физически не может создать вторую строку.
"""
from alembic import op

revision = "e1f2a3b4c5d6"
down_revision = "c9d1e4f7a2b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Дедупликация: для каждой пары (user, salon|master) живёт строка с min(id)
    op.execute("""
        DELETE FROM favorites f USING favorites f2
        WHERE f.id > f2.id
          AND f.user_id = f2.user_id
          AND f.salon_id IS NOT DISTINCT FROM f2.salon_id
          AND f.master_id IS NOT DISTINCT FROM f2.master_id
    """)
    op.create_index(
        "uq_favorite_user_salon", "favorites", ["user_id", "salon_id"],
        unique=True, postgresql_where="salon_id IS NOT NULL",
    )
    op.create_index(
        "uq_favorite_user_master", "favorites", ["user_id", "master_id"],
        unique=True, postgresql_where="master_id IS NOT NULL",
    )


def downgrade() -> None:
    op.drop_index("uq_favorite_user_master", table_name="favorites")
    op.drop_index("uq_favorite_user_salon", table_name="favorites")
