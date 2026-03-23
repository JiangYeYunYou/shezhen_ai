"""add_advice_column_to_diagnosis

Revision ID: 6c0e5f172ac9
Revises: 6e95eed58b47
Create Date: 2026-03-23 12:05:46.358940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6c0e5f172ac9'
down_revision: Union[str, Sequence[str], None] = '6e95eed58b47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'diagnosis',
        sa.Column('advice', sa.String(2000), nullable=False, server_default='[]')
    )


def downgrade() -> None:
    op.drop_column('diagnosis', 'advice')
