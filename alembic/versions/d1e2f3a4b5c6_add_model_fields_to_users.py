"""add model fields to users

Revision ID: d1e2f3a4b5c6
Revises: a6d288d27c6e
Create Date: 2026-07-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, None] = 'a6d288d27c6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_model", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("users", sa.Column("model_photo_url", sa.String(length=500), nullable=True))
    op.add_column("users", sa.Column("model_bio", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("model_looking_for", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "model_looking_for")
    op.drop_column("users", "model_bio")
    op.drop_column("users", "model_photo_url")
    op.drop_column("users", "is_model")
