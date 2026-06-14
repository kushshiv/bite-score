from sqlalchemy import Boolean, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class StructuredScore(Base):
    __tablename__ = "structured_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), unique=True, nullable=False)
    cleanliness: Mapped[float] = mapped_column(Float, nullable=False)
    staff_hygiene: Mapped[float] = mapped_column(Float, nullable=False)
    food_handling: Mapped[float] = mapped_column(Float, nullable=False)
    packaging: Mapped[float] = mapped_column(Float, nullable=False)
    water_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    oil_freshness_concern: Mapped[bool] = mapped_column(Boolean, default=False)
    taste_optional: Mapped[float | None] = mapped_column(Float)

    review: Mapped["Review"] = relationship(back_populates="structured_score")
