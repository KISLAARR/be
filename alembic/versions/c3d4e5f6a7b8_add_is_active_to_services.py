"""add is_active to services (soft-delete)

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-07-21 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("services", sa.Column(
        "is_active", sa.Boolean(), nullable=False, server_default="true"
    ))


def downgrade() -> None:
    op.drop_column("services", "is_active")
