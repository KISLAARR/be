"""merge heads: userrole+BUSINESS admin_audit NOT NULL / salon_members flexible permissions

Revision ID: a7b154fe10ae
Revises: d4e5f6a7b8c9, f3a9c7d1e5b2
Create Date: 2026-07-16 00:57:39.857947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7b154fe10ae'
down_revision: Union[str, None] = ('d4e5f6a7b8c9', 'f3a9c7d1e5b2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
