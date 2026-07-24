"""add model moderation status to users (approval flow like salons)

Revision ID: a4b5c6d7e8f9
Revises: f3a4b5c6d7e8
Create Date: 2026-07-23 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4b5c6d7e8f9'
down_revision: Union[str, None] = 'f3a4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_status = sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='modelmoderationstatus')


def upgrade() -> None:
    bind = op.get_bind()
    _status.create(bind, checkfirst=True)
    op.add_column('users', sa.Column(
        'model_moderation_status',
        sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='modelmoderationstatus', create_type=False),
        server_default='PENDING', nullable=False,
    ))
    op.add_column('users', sa.Column('model_rejection_reason', sa.Text(), nullable=True))
    # У кого уже включён is_model (заведён до появления модерации) — считаем
    # одобренными задним числом, иначе они молча исчезнут из ленты у салонов.
    op.execute("UPDATE users SET model_moderation_status = 'APPROVED' WHERE is_model = true")


def downgrade() -> None:
    op.drop_column('users', 'model_rejection_reason')
    op.drop_column('users', 'model_moderation_status')
    _status.drop(op.get_bind(), checkfirst=True)
