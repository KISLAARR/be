"""model matching moves from per-master to per-service (drop offer_*, add service_id)

Revision ID: b9c0d1e2f3a4
Revises: c6d7e8f9a0b1
Create Date: 2026-07-24 18:00:00.000000

Мэтч теперь на паре (модель, конкретная опубликованная услуга), а не
(модель, мастер) — цена/длительность берутся из Service напрямую, отдельного
шага "оффер" больше нет. Таблица создана в этой же (ещё не выпущенной)
фиче в текущем спринте, реальных данных в проде нет — пересоздаём с нуля,
а не городим ALTER-миграцию с бэкфиллом.

CREATE TABLE — чистым raw SQL (op.execute), а не op.create_table(): даже с
create_type=False на колонке-Enum, Alembic всё равно пытается пересоздать
Postgres-тип modelmatchstatus (стабильно валится DuplicateObjectError, тип
уже существует от исходной миграции f3a4b5c6d7e8). Raw SQL полностью
обходит эту логику — тип не трогаем вообще, 'offered' остаётся в нём
неиспользуемым значением (как раньше поступили с UserRole.MODEL/
ModelModerationStatus), Python-enum ModelMatchStatus его больше не содержит."""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b9c0d1e2f3a4'
down_revision: Union[str, None] = 'c6d7e8f9a0b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TABLE model_matches")
    op.execute("""
        CREATE TABLE model_matches (
            id SERIAL PRIMARY KEY,
            model_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
            master_id INTEGER NOT NULL REFERENCES masters(id) ON DELETE CASCADE,
            salon_id INTEGER NOT NULL REFERENCES salons(id) ON DELETE CASCADE,
            model_liked BOOLEAN,
            model_liked_at TIMESTAMPTZ,
            salon_liked BOOLEAN,
            salon_liked_at TIMESTAMPTZ,
            salon_liked_by_id INTEGER REFERENCES users(id),
            status modelmatchstatus NOT NULL DEFAULT 'PENDING',
            matched_at TIMESTAMPTZ,
            chosen_slot TIMESTAMP,
            booking_id INTEGER REFERENCES bookings(id) ON DELETE SET NULL,
            declined_by VARCHAR(10),
            declined_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT now(),
            CONSTRAINT uq_model_match_pair UNIQUE (model_user_id, service_id)
        )
    """)
    op.execute("CREATE INDEX ix_model_matches_model_status ON model_matches (model_user_id, status)")
    op.execute("CREATE INDEX ix_model_matches_salon_status ON model_matches (salon_id, status)")


def downgrade() -> None:
    op.execute("DROP TABLE model_matches")
    op.execute("""
        CREATE TABLE model_matches (
            id SERIAL PRIMARY KEY,
            model_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            master_id INTEGER NOT NULL REFERENCES masters(id) ON DELETE CASCADE,
            salon_id INTEGER NOT NULL REFERENCES salons(id) ON DELETE CASCADE,
            model_liked BOOLEAN,
            model_liked_at TIMESTAMPTZ,
            salon_liked BOOLEAN,
            salon_liked_at TIMESTAMPTZ,
            salon_liked_by_id INTEGER REFERENCES users(id),
            status modelmatchstatus NOT NULL DEFAULT 'PENDING',
            matched_at TIMESTAMPTZ,
            offer_price INTEGER,
            offer_service_id INTEGER REFERENCES services(id),
            offer_slots JSON,
            offered_at TIMESTAMPTZ,
            offered_by_id INTEGER REFERENCES users(id),
            chosen_slot TIMESTAMP,
            booking_id INTEGER REFERENCES bookings(id) ON DELETE SET NULL,
            declined_by VARCHAR(10),
            declined_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT now(),
            CONSTRAINT uq_model_match_pair UNIQUE (model_user_id, master_id)
        )
    """)
    op.execute("CREATE INDEX ix_model_matches_model_status ON model_matches (model_user_id, status)")
    op.execute("CREATE INDEX ix_model_matches_salon_status ON model_matches (salon_id, status)")
