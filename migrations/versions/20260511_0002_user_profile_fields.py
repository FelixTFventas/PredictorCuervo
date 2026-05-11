"""Add user profile fields.

Revision ID: 20260511_0002
Revises: 20260509_0001
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_0002"
down_revision = "20260509_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("display_name", sa.String(length=80), nullable=True))
    op.add_column("user", sa.Column("avatar_url", sa.String(length=500), nullable=True))


def downgrade():
    op.drop_column("user", "avatar_url")
    op.drop_column("user", "display_name")
