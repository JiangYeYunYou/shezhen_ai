"""Initial migration

Revision ID: 000000000001
Revises:
Create Date: 2026-04-29 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '000000000001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建 user 和 diagnosis 两张核心表，与 SQLAlchemy 模型完全对齐。"""

    # ------------------------------
    # user 表
    # ------------------------------
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=50, collation='utf8mb4_unicode_ci'), nullable=False),
        sa.Column('password', sa.String(length=255, collation='utf8mb4_unicode_ci'), nullable=False),
        sa.Column('salt', sa.String(length=64, collation='utf8mb4_unicode_ci'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)

    # ------------------------------
    # diagnosis 表
    # ------------------------------
    op.create_table(
        'diagnosis',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tongue_analysis', sa.Text(collation='utf8mb4_unicode_ci'), nullable=False),
        sa.Column('syndromes', sa.Text(collation='utf8mb4_unicode_ci'), nullable=False),
        sa.Column('constitution', sa.Text(collation='utf8mb4_unicode_ci'), nullable=False),
        sa.Column('health_score', sa.Text(collation='utf8mb4_unicode_ci'), nullable=False, server_default='{}'),
        sa.Column('advice', sa.Text(collation='utf8mb4_unicode_ci'), nullable=False, server_default=''),
        sa.Column('tongue_surface_image', mysql.LONGBLOB(), nullable=True),
        sa.Column('tongue_bottom_image', mysql.LONGBLOB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    op.create_index('ix_diagnosis_user_id', 'diagnosis', ['user_id'])
    op.create_index('ix_diagnosis_created_at', 'diagnosis', ['created_at'])


def downgrade() -> None:
    """回滚：先删 diagnosis（含外键），再删 user。"""
    op.drop_index('ix_diagnosis_created_at', table_name='diagnosis')
    op.drop_index('ix_diagnosis_user_id', table_name='diagnosis')
    op.drop_table('diagnosis')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
