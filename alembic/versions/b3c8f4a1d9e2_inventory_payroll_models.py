"""add inventory (mini-warehouse per master, movements, audits), payroll
(master rate + manual bonuses/penalties), salon_models, client_notes;
bookings.consumption_reported; manage_inventory/manage_payroll permissions

Revision ID: b3c8f4a1d9e2
Revises: a7b154fe10ae
Create Date: 2026-07-16
"""
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b3c8f4a1d9e2"
down_revision: Union[str, None] = "a7b154fe10ae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- bookings.consumption_reported ---
    op.add_column(
        "bookings",
        sa.Column("consumption_reported", sa.Boolean(), nullable=False, server_default="false"),
    )

    # --- inventory_items: мини-склад мастера ---
    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("master_id", sa.Integer(), sa.ForeignKey("masters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("cost_per_unit", sa.Integer(), nullable=False),
        sa.Column("min_quantity", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )

    # --- inventory_movements: журнал (приход/списание/корректировка) ---
    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("RECEIPT", "CONSUMPTION", "ADJUSTMENT", name="inventorymovementtype"), nullable=False),
        sa.Column("delta", sa.Float(), nullable=False),
        sa.Column("unit_cost_snapshot", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_inventory_movements_item", "inventory_movements", ["item_id"])
    op.create_index("ix_inventory_movements_booking", "inventory_movements", ["booking_id"])

    # --- inventory_audits / inventory_audit_items: акты инвентаризации ---
    op.create_table(
        "inventory_audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("master_id", sa.Integer(), sa.ForeignKey("masters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "CONFIRMED", name="inventoryauditstatus"), nullable=False, server_default="DRAFT"),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_table(
        "inventory_audit_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("audit_id", sa.Integer(), sa.ForeignKey("inventory_audits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expected_quantity", sa.Float(), nullable=False),
        sa.Column("actual_quantity", sa.Float(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
    )

    # --- master_payroll_settings / payroll_adjustments ---
    op.create_table(
        "master_payroll_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("master_id", sa.Integer(), sa.ForeignKey("masters.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("base_salary", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("commission_percent", sa.Float(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_table(
        "payroll_adjustments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("master_id", sa.Integer(), sa.ForeignKey("masters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("period_month", sa.DateTime(timezone=False), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_payroll_adjustments_master_period", "payroll_adjustments", ["master_id", "period_month"])

    # --- salon_models: promo-модели, привязанные к салону ---
    op.create_table(
        "salon_models",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("salon_id", sa.Integer(), sa.ForeignKey("salons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("stage_name", sa.String(100), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.UniqueConstraint("salon_id", "user_id", name="uq_salon_model"),
    )

    # --- client_notes: заметки на карточке клиента ---
    op.create_table(
        "client_notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("salon_id", sa.Integer(), sa.ForeignKey("salons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_client_notes_salon_client", "client_notes", ["salon_id", "client_id"])

    # --- data-migration: добавить manage_inventory/manage_payroll в permissions
    # существующих salon_members (owner -> True/True, admin -> False/False,
    # как в OWNER_DEFAULT_PERMISSIONS/ADMIN_DEFAULT_PERMISSIONS) ---
    conn = op.get_bind()
    members = conn.execute(sa.text("SELECT id, role, permissions FROM salon_members")).fetchall()
    for member_id, role, permissions in members:
        perms = dict(permissions or {})
        is_owner = str(role).upper() == "OWNER"
        perms.setdefault("manage_inventory", is_owner)
        perms.setdefault("manage_payroll", is_owner)
        conn.execute(
            sa.text("UPDATE salon_members SET permissions = CAST(:permissions AS JSON) WHERE id = :id"),
            {"permissions": json.dumps(perms), "id": member_id},
        )


def downgrade() -> None:
    op.drop_index("ix_client_notes_salon_client", table_name="client_notes")
    op.drop_table("client_notes")

    op.drop_table("salon_models")

    op.drop_index("ix_payroll_adjustments_master_period", table_name="payroll_adjustments")
    op.drop_table("payroll_adjustments")
    op.drop_table("master_payroll_settings")

    op.drop_table("inventory_audit_items")
    op.drop_table("inventory_audits")
    op.execute("DROP TYPE IF EXISTS inventoryauditstatus")

    op.drop_index("ix_inventory_movements_booking", table_name="inventory_movements")
    op.drop_index("ix_inventory_movements_item", table_name="inventory_movements")
    op.drop_table("inventory_movements")
    op.execute("DROP TYPE IF EXISTS inventorymovementtype")

    op.drop_table("inventory_items")

    op.drop_column("bookings", "consumption_reported")
