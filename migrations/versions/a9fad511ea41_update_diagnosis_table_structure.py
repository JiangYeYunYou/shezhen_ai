"""update_diagnosis_table_structure

Revision ID: a9fad511ea41
Revises: 6c0e5f172ac9
Create Date: 2026-04-10 09:09:08.113003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = 'a9fad511ea41'
down_revision: Union[str, Sequence[str], None] = '6c0e5f172ac9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('diagnosis', sa.Column('tongue_analysis', sa.Text(), nullable=True))
    op.add_column('diagnosis', sa.Column('syndromes', sa.Text(), nullable=True))
    op.add_column('diagnosis', sa.Column('constitution', sa.Text(), nullable=True))
    
    op.execute("""
        UPDATE diagnosis 
        SET tongue_analysis = '{}', 
            syndromes = '[]', 
            constitution = '{}'
    """)
    
    op.alter_column('diagnosis', 'tongue_analysis', 
                    existing_type=mysql.TEXT(collation='utf8mb4_unicode_ci'),
                    nullable=False)
    op.alter_column('diagnosis', 'syndromes', 
                    existing_type=mysql.TEXT(collation='utf8mb4_unicode_ci'),
                    nullable=False)
    op.alter_column('diagnosis', 'constitution', 
                    existing_type=mysql.TEXT(collation='utf8mb4_unicode_ci'),
                    nullable=False)
    
    op.drop_column('diagnosis', 'signs')
    op.drop_column('diagnosis', 'symptoms')
    
    op.alter_column('diagnosis', 'advice', 
                    existing_type=mysql.TEXT(collation='utf8mb4_unicode_ci'),
                    nullable=False,
                    server_default='')


def downgrade() -> None:
    op.add_column('diagnosis', sa.Column('signs', sa.Text(), nullable=True))
    op.add_column('diagnosis', sa.Column('symptoms', sa.Text(), nullable=True))
    
    op.execute("""
        UPDATE diagnosis 
        SET signs = '[]', 
            symptoms = '[]'
    """)
    
    op.alter_column('diagnosis', 'signs', 
                    existing_type=mysql.TEXT(collation='utf8mb4_unicode_ci'),
                    nullable=False)
    op.alter_column('diagnosis', 'symptoms', 
                    existing_type=mysql.TEXT(collation='utf8mb4_unicode_ci'),
                    nullable=False)
    
    op.drop_column('diagnosis', 'tongue_analysis')
    op.drop_column('diagnosis', 'syndromes')
    op.drop_column('diagnosis', 'constitution')
    
    op.alter_column('diagnosis', 'advice', 
                    existing_type=mysql.TEXT(collation='utf8mb4_unicode_ci'),
                    nullable=True)
