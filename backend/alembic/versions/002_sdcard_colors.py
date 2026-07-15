"""add sd card two-color fields

Revision ID: 002
Revises: 001
Create Date: 2026-07-14
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("storage_mediums", sa.Column("color_primary", sa.String, nullable=True))
    op.add_column("storage_mediums", sa.Column("color_secondary", sa.String, nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("storage_mediums") as batch_op:
        batch_op.drop_column("color_primary")
        batch_op.drop_column("color_secondary")
