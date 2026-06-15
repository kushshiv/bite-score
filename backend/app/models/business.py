from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import BusinessStatus, BusinessType


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    business_type: Mapped[BusinessType] = mapped_column(Enum(BusinessType), default=BusinessType.RESTAURANT)
    description: Mapped[str | None] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[BusinessStatus] = mapped_column(Enum(BusinessStatus), default=BusinessStatus.ACTIVE)
    claimed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    category: Mapped["Category | None"] = relationship(back_populates="businesses")
    location: Mapped["Location | None"] = relationship(back_populates="business", uselist=False)
    reviews: Mapped[list["Review"]] = relationship(back_populates="business")
    badges: Mapped[list["VerificationBadge"]] = relationship(back_populates="business")
    evidence_uploads: Mapped[list["EvidenceUpload"]] = relationship(back_populates="business")
    claim_requests: Mapped[list["ClaimRequest"]] = relationship(back_populates="business")
