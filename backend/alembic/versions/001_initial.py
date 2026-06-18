"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role = postgresql.ENUM(
    "user",
    "moderator",
    "business_owner",
    "admin",
    name="userrole",
    create_type=False,
)
business_type = postgresql.ENUM(
    "restaurant",
    "street_vendor",
    "cafe",
    "food_court",
    "bakery",
    "cloud_kitchen",
    "other",
    name="businesstype",
    create_type=False,
)
business_status = postgresql.ENUM(
    "active",
    "under_review",
    "hidden",
    name="businessstatus",
    create_type=False,
)
visit_type = postgresql.ENUM(
    "dine_in",
    "takeaway",
    "delivery",
    name="visittype",
    create_type=False,
)
review_status = postgresql.ENUM(
    "pending",
    "approved",
    "hidden",
    "flagged",
    name="reviewstatus",
    create_type=False,
)
claim_status = postgresql.ENUM(
    "pending",
    "approved",
    "rejected",
    name="claimstatus",
    create_type=False,
)
badge_type = postgresql.ENUM(
    "claimed",
    "verified",
    "high_confidence",
    "under_review",
    name="badgetype",
    create_type=False,
)
flag_target_type = postgresql.ENUM(
    "review",
    "business",
    "evidence",
    name="flagtargettype",
    create_type=False,
)
flag_status = postgresql.ENUM(
    "open",
    "resolved",
    "dismissed",
    name="flagstatus",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    business_type.create(bind, checkfirst=True)
    business_status.create(bind, checkfirst=True)
    visit_type.create(bind, checkfirst=True)
    review_status.create(bind, checkfirst=True)
    claim_status.create(bind, checkfirst=True)
    badge_type.create(bind, checkfirst=True)
    flag_target_type.create(bind, checkfirst=True)
    flag_status.create(bind, checkfirst=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_categories_slug"), "categories", ["slug"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column(
            "role",
            user_role,
            nullable=False,
            server_default="user",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "admin_audits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "businesses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column(
            "business_type",
            business_type,
            nullable=False,
            server_default="restaurant",
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cover_image_url", sa.String(length=500), nullable=True),
        sa.Column(
            "status",
            business_status,
            nullable=False,
            server_default="active",
        ),
        sa.Column("claimed_by_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["claimed_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_businesses_name"), "businesses", ["name"], unique=False)
    op.create_index(op.f("ix_businesses_slug"), "businesses", ["slug"], unique=True)

    op.create_table(
        "report_flags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reporter_id", sa.Integer(), nullable=True),
        sa.Column("target_type", flag_target_type, nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "status",
            flag_status,
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["reporter_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "claim_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            claim_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("documents", sa.Text(), nullable=True),
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

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id"),
    )
    op.create_index(op.f("ix_locations_city"), "locations", ["city"], unique=False)

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "visit_type",
            visit_type,
            nullable=False,
            server_default="dine_in",
        ),
        sa.Column("visit_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("business_response", sa.Text(), nullable=True),
        sa.Column("consent_given", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "status",
            review_status,
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reviews_business_id"), "reviews", ["business_id"], unique=False)

    op.create_table(
        "verification_badges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("badge_type", badge_type, nullable=False),
        sa.Column("issued_by_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"]),
        sa.ForeignKeyConstraint(["issued_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "evidence_uploads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=True),
        sa.Column("business_id", sa.Integer(), nullable=True),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"]),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "structured_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("cleanliness", sa.Float(), nullable=False),
        sa.Column("staff_hygiene", sa.Float(), nullable=False),
        sa.Column("food_handling", sa.Float(), nullable=False),
        sa.Column("packaging", sa.Float(), nullable=False),
        sa.Column("water_confidence", sa.Float(), nullable=False),
        sa.Column(
            "oil_freshness_concern",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("taste_optional", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["review_id"], ["reviews.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("review_id"),
    )


def downgrade() -> None:
    op.drop_table("structured_scores")
    op.drop_table("evidence_uploads")
    op.drop_table("verification_badges")
    op.drop_index(op.f("ix_reviews_business_id"), table_name="reviews")
    op.drop_table("reviews")
    op.drop_index(op.f("ix_locations_city"), table_name="locations")
    op.drop_table("locations")
    op.drop_table("claim_requests")
    op.drop_table("report_flags")
    op.drop_index(op.f("ix_businesses_slug"), table_name="businesses")
    op.drop_index(op.f("ix_businesses_name"), table_name="businesses")
    op.drop_table("businesses")
    op.drop_table("admin_audits")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_categories_slug"), table_name="categories")
    op.drop_table("categories")

    bind = op.get_bind()
    flag_status.drop(bind, checkfirst=True)
    flag_target_type.drop(bind, checkfirst=True)
    badge_type.drop(bind, checkfirst=True)
    claim_status.drop(bind, checkfirst=True)
    review_status.drop(bind, checkfirst=True)
    visit_type.drop(bind, checkfirst=True)
    business_status.drop(bind, checkfirst=True)
    business_type.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
