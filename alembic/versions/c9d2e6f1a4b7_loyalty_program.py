"""add salon loyalty program: settings, named offers/promo codes,
per-client status/personal discount, bonus points ledger;
bookings.loyalty_source / bonus_points_redeemed

Revision ID: c9d2e6f1a4b7
Revises: b3c8f4a1d9e2
Create Date: 2026-07-17
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c9d2e6f1a4b7"
down_revision: Union[str, None] = "b3c8f4a1d9e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- bookings: что применили при завершении записи ---
    op.add_column("bookings", sa.Column("loyalty_source", sa.String(100), nullable=True))
    op.add_column(
        "bookings",
        sa.Column("bonus_points_redeemed", sa.Integer(), nullable=False, server_default="0"),
    )

    # --- salon_loyalty_settings: 1-1 с salons ---
    op.create_table(
        "salon_loyalty_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("salon_id", sa.Integer(), sa.ForeignKey("salons.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("regular_client_discount_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("regular_client_visits_threshold", sa.Integer(), nullable=True),
        sa.Column("bonus_accrual_percent", sa.Float(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    # --- loyalty_offers: именные скидки/промокоды салона ---
    op.create_table(
        "loyalty_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("salon_id", sa.Integer(), sa.ForeignKey("salons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("discount_percent", sa.Integer(), nullable=False),
        sa.Column("promo_code", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.UniqueConstraint("salon_id", "promo_code", name="uq_loyalty_offer_promo_code"),
    )

    # --- client_loyalty: статус + персональная скидка + баланс баллов на (salon, client) ---
    op.create_table(
        "client_loyalty",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("salon_id", sa.Integer(), sa.ForeignKey("salons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_regular_client", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("regular_client_source", sa.Enum("AUTO", "MANUAL", name="loyaltystatussource"), nullable=True),
        sa.Column("personal_discount_percent", sa.Integer(), nullable=True),
        sa.Column("bonus_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.UniqueConstraint("salon_id", "client_id", name="uq_client_loyalty"),
    )

    # --- loyalty_points_movements: журнал начислений/списаний баллов ---
    op.create_table(
        "loyalty_points_movements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_loyalty_id", sa.Integer(), sa.ForeignKey("client_loyalty.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "type",
            sa.Enum("ACCRUAL", "MANUAL_ADD", "REDEEMED", "MANUAL_REMOVE", name="loyaltypointsmovementtype"),
            nullable=False,
        ),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_loyalty_points_movements_client_loyalty", "loyalty_points_movements", ["client_loyalty_id"])


def downgrade() -> None:
    op.drop_index("ix_loyalty_points_movements_client_loyalty", table_name="loyalty_points_movements")
    op.drop_table("loyalty_points_movements")
    op.execute("DROP TYPE IF EXISTS loyaltypointsmovementtype")

    op.drop_table("client_loyalty")
    op.execute("DROP TYPE IF EXISTS loyaltystatussource")

    op.drop_table("loyalty_offers")
    op.drop_table("salon_loyalty_settings")

    op.drop_column("bookings", "bonus_points_redeemed")
    op.drop_column("bookings", "loyalty_source")
