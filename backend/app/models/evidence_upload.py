from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class EvidenceUpload(Base):
    __tablename__ = "evidence_uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int | None] = mapped_column(ForeignKey("reviews.id"))
    business_id: Mapped[int | None] = mapped_column(ForeignKey("businesses.id"))
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    review: Mapped["Review | None"] = relationship(back_populates="evidence_uploads")
    business: Mapped["Business | None"] = relationship(back_populates="evidence_uploads")
