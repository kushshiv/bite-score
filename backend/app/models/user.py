from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.types import pg_enum
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(pg_enum(UserRole), default=UserRole.USER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    claim_requests: Mapped[list["ClaimRequest"]] = relationship(back_populates="user")
    certification_uploads: Mapped[list["CertificationUpload"]] = relationship(
        back_populates="uploaded_by"
    )
    badge_requests: Mapped[list["BadgeRequest"]] = relationship(back_populates="user")
    admin_audits: Mapped[list["AdminAudit"]] = relationship(back_populates="actor")
