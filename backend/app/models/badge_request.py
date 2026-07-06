from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.types import pg_enum
from app.models.enums import BadgeType, ClaimStatus


class BadgeRequest(Base):
    __tablename__ = "badge_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    badge_type: Mapped[BadgeType] = mapped_column(pg_enum(BadgeType), nullable=False)
    status: Mapped[ClaimStatus] = mapped_column(pg_enum(ClaimStatus), default=ClaimStatus.PENDING)
    notes: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="badge_requests")
    user: Mapped["User"] = relationship(back_populates="badge_requests")
