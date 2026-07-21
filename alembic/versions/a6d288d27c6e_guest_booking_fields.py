"""guest booking fields

Revision ID: a6d288d27c6e
Revises: c3d4e5f6a7b8
Create Date: 2026-07-21 20:13:59.611066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6d288d27c6e'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_guest", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("salons", sa.Column("guest_booking_enabled", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("bookings", sa.Column("guest_manage_token", sa.String(length=64), nullable=True))
    op.add_column("bookings", sa.Column("guest_email", sa.String(length=100), nullable=True))
    op.create_index("ix_bookings_guest_manage_token", "bookings", ["guest_manage_token"])


def downgrade() -> None:
    op.drop_index("ix_bookings_guest_manage_token", table_name="bookings")
    op.drop_column("bookings", "guest_email")
    op.drop_column("bookings", "guest_manage_token")
    op.drop_column("salons", "guest_booking_enabled")
    op.drop_column("users", "is_guest")
