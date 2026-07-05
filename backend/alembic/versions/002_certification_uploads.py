"""Certification uploads for business owners

Revision ID: 002
Revises: 001
Create Date: 2026-06-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

certification_status = postgresql.ENUM(
    "pending",
    "verified",
    "rejected",
    name="certificationstatus",
    create_type=False,
)


def upgrade() -> None:
    certification_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "certification_uploads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            certification_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"]),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_certification_uploads_business_id"),
        "certification_uploads",
        ["business_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_certification_uploads_business_id"), table_name="certification_uploads")
    op.drop_table("certification_uploads")
    certification_status.drop(op.get_bind(), checkfirst=True)
