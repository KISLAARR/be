"""fix_bookings_time_column_drift

Revision ID: 43ebd2352eb2
Revises: d5e8a2c4f9b1
Create Date: 2026-07-17 00:00:00.000000

Миграция 395182833d9c (change_booking_time_to_naive) отмечена как применённая,
но на части баз (в т.ч. локальной dev) колонки bookings.start_time/end_time
физически остались timestamp WITH time zone — из-за этого asyncpg возвращал
tz-aware datetime и падало сравнение с naive datetime.now() на странице
"Мои записи". Здесь чиним фактическое рассогласование схемы, проверяя реальный
тип колонки перед ALTER, чтобы миграция была безопасным no-op там, где
395182833d9c и правда уже сработала (сессия БД — UTC, поэтому
AT TIME ZONE 'UTC' переносит значения без сдвига).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '43ebd2352eb2'
down_revision: Union[str, None] = 'd5e8a2c4f9b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_has_timezone(bind, table: str, column: str) -> bool:
    result = bind.execute(
        sa.text(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_name = :table AND column_name = :column"
        ),
        {"table": table, "column": column},
    ).scalar()
    return result == "timestamp with time zone"


def upgrade() -> None:
    bind = op.get_bind()
    for column in ("start_time", "end_time"):
        if _column_has_timezone(bind, "bookings", column):
            op.execute(
                f"ALTER TABLE bookings ALTER COLUMN {column} "
                f"TYPE timestamp without time zone USING {column} AT TIME ZONE 'UTC'"
            )


def downgrade() -> None:
    bind = op.get_bind()
    for column in ("start_time", "end_time"):
        if not _column_has_timezone(bind, "bookings", column):
            op.execute(
                f"ALTER TABLE bookings ALTER COLUMN {column} "
                f"TYPE timestamp with time zone USING {column} AT TIME ZONE 'UTC'"
            )
