"""create model_matches (мэтчинг модель <-> мастер)

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-07-23 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, None] = 'e2f3a4b5c6d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'model_matches',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('model_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('master_id', sa.Integer(), sa.ForeignKey('masters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('salon_id', sa.Integer(), sa.ForeignKey('salons.id', ondelete='CASCADE'), nullable=False),

        sa.Column('model_liked', sa.Boolean(), nullable=True),
        sa.Column('model_liked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('salon_liked', sa.Boolean(), nullable=True),
        sa.Column('salon_liked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('salon_liked_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),

        sa.Column('status', sa.Enum('PENDING', 'MATCHED', 'OFFERED', 'BOOKED', 'DECLINED', name='modelmatchstatus'),
                  nullable=False, server_default='PENDING'),
        sa.Column('matched_at', sa.DateTime(timezone=True), nullable=True),

        sa.Column('offer_price', sa.Integer(), nullable=True),
        sa.Column('offer_service_id', sa.Integer(), sa.ForeignKey('services.id'), nullable=True),
        sa.Column('offer_slots', sa.JSON(), nullable=True),
        sa.Column('offered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('offered_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),

        sa.Column('chosen_slot', sa.DateTime(timezone=False), nullable=True),
        sa.Column('booking_id', sa.Integer(), sa.ForeignKey('bookings.id', ondelete='SET NULL'), nullable=True),

        sa.Column('declined_by', sa.String(length=10), nullable=True),
        sa.Column('declined_at', sa.DateTime(timezone=True), nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),

        sa.UniqueConstraint('model_user_id', 'master_id', name='uq_model_match_pair'),
    )
    op.create_index('ix_model_matches_model_status', 'model_matches', ['model_user_id', 'status'])
    op.create_index('ix_model_matches_salon_status', 'model_matches', ['salon_id', 'status'])


def downgrade() -> None:
    op.drop_index('ix_model_matches_salon_status', table_name='model_matches')
    op.drop_index('ix_model_matches_model_status', table_name='model_matches')
    op.drop_table('model_matches')
    sa.Enum(name='modelmatchstatus').drop(op.get_bind(), checkfirst=True)
