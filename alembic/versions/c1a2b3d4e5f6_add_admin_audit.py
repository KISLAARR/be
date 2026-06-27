"""add admin_audit table

Revision ID: c1a2b3d4e5f6
Revises: a441e0269dfc
Create Date: 2026-06-28
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c1a2b3d4e5f6"
down_revision = "a441e0269dfc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("target_type", sa.String(length=30), nullable=True),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )
    op.create_index("ix_admin_audit_created", "admin_audit", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_admin_audit_created", table_name="admin_audit")
    op.drop_table("admin_audit")
