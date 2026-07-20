"""add schedule_closures: close a specific calendar date for the whole
salon or a single master (separate from the recurring weekly working_hours)

Revision ID: d5e8a2c4f9b1
Revises: c9d2e6f1a4b7
Create Date: 2026-07-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d5e8a2c4f9b1"
down_revision: Union[str, None] = "c9d2e6f1a4b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "schedule_closures",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("salon_id", sa.Integer(), sa.ForeignKey("salons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("master_id", sa.Integer(), sa.ForeignKey("masters.id", ondelete="CASCADE"), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index(
        "uq_schedule_closure_salon", "schedule_closures", ["salon_id", "date"], unique=True,
        postgresql_where=sa.text("master_id IS NULL"),
    )
    op.create_index(
        "uq_schedule_closure_master", "schedule_closures", ["salon_id", "master_id", "date"], unique=True,
        postgresql_where=sa.text("master_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_schedule_closure_master", table_name="schedule_closures")
    op.drop_index("uq_schedule_closure_salon", table_name="schedule_closures")
    op.drop_table("schedule_closures")
