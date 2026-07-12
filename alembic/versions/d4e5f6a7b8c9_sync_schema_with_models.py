"""userrole: +BUSINESS; admin_audit.created_at NOT NULL

Дрейф «модели против миграций», найденный при разворачивании staging по
миграциям (dev-БД создавалась через create_all и потому маскировала):
  1) в модель UserRole добавили BUSINESS, а enum-миграцию не написали —
     сиды и назначение роли падали с InvalidTextRepresentationError;
  2) admin_audit.created_at в модели NOT NULL, в миграции — nullable.

Revision ID: d4e5f6a7b8c9
Revises: c1a2b3d4e5f6
Create Date: 2026-07-09
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "d4e5f6a7b8c9"
down_revision = "c1a2b3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PG≥12 позволяет ADD VALUE в транзакции; использовать новое значение
    # в ЭТОЙ ЖЕ транзакции нельзя — здесь и не используем
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'BUSINESS'")
    op.alter_column(
        "admin_audit",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        existing_server_default=sa.text("now()"),
    )


def downgrade() -> None:
    # Удалить значение из enum PostgreSQL не умеет — оставляем (безвредно)
    op.alter_column(
        "admin_audit",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
