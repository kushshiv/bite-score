"""Badge requests from business owners

Revision ID: 003
Revises: 002
Create Date: 2026-06-16
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

badge_type = postgresql.ENUM(
    "claimed",
    "verified",
    "high_confidence",
    "under_review",
    name="badgetype",
    create_type=False,
)
claim_status = postgresql.ENUM(
    "pending",
    "approved",
    "rejected",
    name="claimstatus",
    create_type=False,
)


def upgrade() -> None:
    op.create_table(
        "badge_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("badge_type", badge_type, nullable=False),
        sa.Column(
            "status",
            claim_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_badge_requests_business_id"),
        "badge_requests",
        ["business_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_badge_requests_business_id"), table_name="badge_requests")
    op.drop_table("badge_requests")
