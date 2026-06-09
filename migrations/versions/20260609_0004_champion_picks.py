"""Add champion picks.

Revision ID: 20260609_0004
Revises: 20260609_0003
Create Date: 2026-06-09
"""

from alembic import op
import sqlalchemy as sa


revision = "20260609_0004"
down_revision = "20260609_0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "champion_pick",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("team_name", sa.String(length=80), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="one_champion_pick_per_user"),
    )
    op.create_table(
        "tournament_setting",
        sa.Column("key", sa.String(length=80), nullable=False),
        sa.Column("value", sa.String(length=160), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade():
    op.drop_table("tournament_setting")
    op.drop_table("champion_pick")
