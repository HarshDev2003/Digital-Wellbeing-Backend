"""add_role_to_users

Revision ID: 66db1c2af1e5
Revises: 001_initial_schema
Create Date: 2026-11-22 05:48:52.621042+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66db1c2af1e5'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('role', sa.String(length=32), nullable=False, server_default='user'),
    )


def downgrade() -> None:
    op.drop_column('users', 'role')
