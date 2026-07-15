"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-14
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String, unique=True, nullable=False, index=True),
        sa.Column("email", sa.String, unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column("is_admin", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "storage_mediums",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", sa.Enum("local", "sdcard", name="storagetype"), nullable=False),
        sa.Column("label", sa.String, nullable=False),
        sa.Column("brand", sa.String, nullable=True),
        sa.Column("model", sa.String, nullable=True),
        sa.Column("size_gb", sa.Float, nullable=True),
        sa.Column("free_gb", sa.Float, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("color", sa.String, default="#6366f1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "games",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("storage_medium_id", sa.Integer, sa.ForeignKey("storage_mediums.id"), nullable=False),
        sa.Column("igdb_id", sa.Integer, nullable=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("cover_url", sa.String, nullable=True),
        sa.Column("genres", sa.String, nullable=True),
        sa.Column("release_year", sa.Integer, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("rating", sa.Float, nullable=True),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "system_settings",
        sa.Column("key", sa.String, primary_key=True),
        sa.Column("value", sa.String, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("system_settings")
    op.drop_table("games")
    op.drop_table("storage_mediums")
    op.drop_table("users")
