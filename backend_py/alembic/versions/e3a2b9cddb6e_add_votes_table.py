"""add votes table

Revision ID: e3a2b9cddb6e
Revises: 0950be30c72b
Create Date: 2025-06-22 22:30:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e3a2b9cddb6e'
down_revision = '0950be30c72b'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'votes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('spot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('spots.id', ondelete='CASCADE'), nullable=False),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('user_id', 'spot_id', name='uq_user_spot_vote'),
    )

def downgrade():
    op.drop_table('votes') 