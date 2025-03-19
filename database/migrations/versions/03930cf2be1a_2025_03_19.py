"""2025-03-19

Revision ID: 03930cf2be1a
Revises: 
Create Date: 2025-03-19 16:21:21.549249

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '03930cf2be1a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conversation_session',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('session_title', sa.String(length=255), nullable=False),
    sa.Column('register_at', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('provider_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('website', sa.String(length=255), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=True),
    sa.Column('group', sa.String(length=100), nullable=True),
    sa.Column('register_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('api_key_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('provider_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('api_key', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('create_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('usage_limit', sa.Integer(), nullable=True),
    sa.Column('usage_count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['provider_id'], ['provider_table.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user_table.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('api_key')
    )
    op.create_table('project_table',
    sa.Column('project_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_email', sa.String(length=255), nullable=False),
    sa.Column('project_name', sa.String(length=255), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('provider', sa.String(length=255), nullable=True),
    sa.Column('ai_model', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['user_email'], ['user_table.email'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('project_id')
    )
    op.create_table('conversation_logs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('user_email', sa.String(length=255), nullable=False),
    sa.Column('message_role', sa.String(length=255), nullable=False),
    sa.Column('conversation', sa.Text(), nullable=False),
    sa.Column('vector_memory', postgresql.ARRAY(sa.Float()), nullable=True),
    sa.Column('request_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['project_table.project_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['session_id'], ['conversation_session.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_email'], ['user_table.email'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('project_info_base',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('user_email', sa.String(length=255), nullable=False),
    sa.Column('file_url', sa.Text(), nullable=True),
    sa.Column('file', postgresql.BYTEA(), nullable=True),
    sa.Column('vector_memory', postgresql.ARRAY(sa.Integer()), nullable=True),
    sa.Column('upload_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['project_table.project_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_email'], ['user_table.email'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('project_info_base')
    op.drop_table('conversation_logs')
    op.drop_table('project_table')
    op.drop_table('api_key_table')
    op.drop_table('user_table')
    op.drop_table('provider_table')
    op.drop_table('conversation_session')
    # ### end Alembic commands ###
