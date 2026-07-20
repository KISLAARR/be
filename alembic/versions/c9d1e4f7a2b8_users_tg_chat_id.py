"""users.tg_chat_id — привязка Telegram для уведомлений

Revision ID: c9d1e4f7a2b8
Revises: 43ebd2352eb2
Create Date: 2026-07-17

Заполняется ботом (@rumi_beauty_bot) при подтверждении номера или через
отдельную привязку /start. BigInteger — телеграмовские chat_id не влезают
в int32. NULL = Telegram не привязан, уведомления не шлются.
"""
from alembic import op
import sqlalchemy as sa

revision = "c9d1e4f7a2b8"
down_revision = "43ebd2352eb2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("tg_chat_id", sa.BigInteger(), nullable=True))
    op.create_index("ix_users_tg_chat_id", "users", ["tg_chat_id"])


def downgrade() -> None:
    op.drop_index("ix_users_tg_chat_id", table_name="users")
    op.drop_column("users", "tg_chat_id")
