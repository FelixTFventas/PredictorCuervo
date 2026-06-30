"""Add manual match winner.

Revision ID: 20260630_0005
Revises: 20260609_0004
Create Date: 2026-06-30
"""

from alembic import op
import sqlalchemy as sa


revision = "20260630_0005"
down_revision = "20260609_0004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("match", sa.Column("winner_team", sa.String(length=80), nullable=True))


def downgrade():
    op.drop_column("match", "winner_team")
