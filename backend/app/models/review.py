from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.db.types import pg_enum
from app.models.enums import ReviewStatus, VisitType


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    visit_type: Mapped[VisitType] = mapped_column(pg_enum(VisitType), default=VisitType.DINE_IN)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    business_response: Mapped[str | None] = mapped_column(Text)
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[ReviewStatus] = mapped_column(
        pg_enum(ReviewStatus), default=ReviewStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    business: Mapped["Business"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")
    structured_score: Mapped["StructuredScore | None"] = relationship(
        back_populates="review", uselist=False
    )
    evidence_uploads: Mapped[list["EvidenceUpload"]] = relationship(back_populates="review")
