"""Initial schema.

Revision ID: 20260509_0001
Revises:
Create Date: 2026-05-09
"""

from alembic import op
import sqlalchemy as sa


revision = "20260509_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=160), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "match",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("home_team", sa.String(length=80), nullable=False),
        sa.Column("away_team", sa.String(length=80), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("group_name", sa.String(length=40), nullable=False, server_default="Fase de grupos"),
        sa.Column("venue", sa.String(length=120), nullable=False, server_default="Sede por confirmar"),
        sa.Column("api_id", sa.String(length=80), nullable=True),
        sa.Column("competition", sa.String(length=120), nullable=False, server_default="FIFA World Cup"),
        sa.Column("season", sa.String(length=20), nullable=False, server_default="2026"),
        sa.Column("round_name", sa.String(length=80), nullable=False, server_default="Fecha por confirmar"),
        sa.Column("stage", sa.String(length=80), nullable=False, server_default="Fase de grupos"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="scheduled"),
        sa.Column("last_synced_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("api_id"),
    )
    op.create_table(
        "prediction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("pred_home_score", sa.Integer(), nullable=False),
        sa.Column("pred_away_score", sa.Integer(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["match.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "match_id", name="one_prediction_per_match"),
    )


def downgrade():
    op.drop_table("prediction")
    op.drop_table("match")
    op.drop_table("user")
