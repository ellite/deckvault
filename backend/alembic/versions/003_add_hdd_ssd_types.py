"""add hdd and ssd storage types

Revision ID: 003
Revises: 002
Create Date: 2026-07-14
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_ENUM = sa.Enum("local", "sdcard", "hdd", "ssd", name="storagetype")
OLD_ENUM = sa.Enum("local", "sdcard", name="storagetype")


def upgrade() -> None:
    with op.batch_alter_table("storage_mediums") as batch_op:
        batch_op.alter_column("type", type_=NEW_ENUM, existing_type=OLD_ENUM)


def downgrade() -> None:
    with op.batch_alter_table("storage_mediums") as batch_op:
        batch_op.alter_column("type", type_=OLD_ENUM, existing_type=NEW_ENUM)
