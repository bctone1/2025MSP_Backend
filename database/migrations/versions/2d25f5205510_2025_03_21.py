"""2025-03-21

Revision ID: 2d25f5205510
Revises: 
Create Date: 2025-03-21 16:05:06.912731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '2d25f5205510'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('conversation_logs', 'vector_memory',
               existing_type=postgresql.ARRAY(sa.DOUBLE_PRECISION(precision=53)),
               type_=Vector(dim=1536),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    op.alter_column('conversation_logs', 'vector_memory',
               existing_type=postgresql.ARRAY(sa.DOUBLE_PRECISION(precision=53)),
               type_=Vector(dim=1536),
               existing_nullable=True)
    # ### end Alembic commands ###
