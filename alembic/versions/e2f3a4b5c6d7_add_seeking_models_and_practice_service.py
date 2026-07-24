"""add seeking_models to masters, is_model_practice to services

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-07-23 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2f3a4b5c6d7'
down_revision: Union[str, None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("masters", sa.Column("seeking_models", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("masters", sa.Column("seeking_models_description", sa.Text(), nullable=True))
    op.add_column("services", sa.Column("is_model_practice", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    op.drop_column("services", "is_model_practice")
    op.drop_column("masters", "seeking_models_description")
    op.drop_column("masters", "seeking_models")
