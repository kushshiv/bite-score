from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import (
    BadgeType,
    BusinessStatus,
    BusinessType,
    CertificationStatus,
    ClaimStatus,
    FlagStatus,
    FlagTargetType,
    ReviewStatus,
    UserRole,
    VisitType,
)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str | None
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class LocationOut(BaseModel):
    address: str | None
    city: str
    country: str
    latitude: float | None = None
    longitude: float | None = None

    model_config = {"from_attributes": True}


class BadgeOut(BaseModel):
    badge_type: BadgeType
    created_at: datetime

    model_config = {"from_attributes": True}


class ScoreBreakdown(BaseModel):
    overall: float
    overall_percent: float
    review_count: int
    breakdown: dict[str, float]
    methodology: str
    trust_indicators: list[str]


class ScoreTrendPoint(BaseModel):
    period_end: date
    label: str
    overall: float
    overall_percent: float
    review_count: int


class ScoreTrendOut(BaseModel):
    points: list[ScoreTrendPoint]
    weeks: int


class BusinessListItem(BaseModel):
    id: int
    name: str
    slug: str
    business_type: BusinessType
    category: CategoryOut | None
    location: LocationOut | None
    cover_image_url: str | None = None
    overall_score: float = 0
    overall_percent: float = 0
    review_count: int = 0
    distance_km: float | None = None
    badges: list[BadgeOut] = []


class CategoryFacet(BaseModel):
    slug: str
    name: str
    count: int


class BusinessFacets(BaseModel):
    total: int
    high_trust: int
    verified: int
    safe_to_eat: int
    categories: list[CategoryFacet]


class BusinessCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    city: str = Field(min_length=2, max_length=100)
    country: str = Field(min_length=2, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    category: str = Field(min_length=2, max_length=100)
    business_type: BusinessType = BusinessType.RESTAURANT
    description: str | None = Field(default=None, max_length=2000)
    latitude: float | None = None
    longitude: float | None = None
    acknowledge_similar: bool = False


class SimilarBusinessMatch(BaseModel):
    id: int
    name: str
    slug: str
    similarity: float
    match_type: str


class DuplicateBusinessErrorDetail(BaseModel):
    message: str
    matches: list[SimilarBusinessMatch]
    allow_confirm: bool = False


class BusinessDetail(BusinessListItem):
    description: str | None
    status: BusinessStatus
    claimed: bool = False
    score: ScoreBreakdown


class StructuredScoreIn(BaseModel):
    cleanliness: float = Field(ge=1, le=5)
    staff_hygiene: float = Field(ge=1, le=5)
    food_handling: float = Field(ge=1, le=5)
    packaging: float = Field(ge=1, le=5)
    water_confidence: float = Field(ge=1, le=5)
    oil_freshness_concern: bool = False
    taste_optional: float | None = Field(default=None, ge=1, le=5)


class ReviewCreate(BaseModel):
    business_id: int
    visit_type: VisitType
    visit_date: date
    notes: str | None = None
    consent_given: bool
    structured_score: StructuredScoreIn


class StructuredScoreOut(StructuredScoreIn):
    model_config = {"from_attributes": True}


class ReviewOut(BaseModel):
    id: int
    business_id: int
    user_id: int
    user_name: str | None = None
    visit_type: VisitType
    visit_date: date
    notes: str | None
    business_response: str | None
    status: ReviewStatus
    structured_score: StructuredScoreOut | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EvidenceOut(BaseModel):
    id: int
    file_url: str
    mime_type: str
    verified: bool
    created_at: datetime


class ReviewModerationItem(BaseModel):
    id: int
    business_id: int
    business_name: str
    business_slug: str
    visit_type: VisitType
    visit_date: date
    notes: str | None
    reviewer_name: str | None
    oil_freshness_concern: bool
    created_at: datetime


class EvidenceModerationItem(BaseModel):
    id: int
    file_url: str
    mime_type: str
    verified: bool
    review_id: int | None
    business_id: int | None
    business_name: str | None
    business_slug: str | None
    created_at: datetime


class CertificationOut(BaseModel):
    id: int
    title: str
    file_url: str
    mime_type: str
    status: CertificationStatus
    created_at: datetime


class CertificationListOut(BaseModel):
    has_verified_badge: bool
    certifications: list[CertificationOut]


class CertificationModerationItem(BaseModel):
    id: int
    title: str
    file_url: str
    mime_type: str
    status: CertificationStatus
    business_id: int
    business_name: str
    business_slug: str
    created_at: datetime


class BadgeRequestCreate(BaseModel):
    notes: str | None = Field(default=None, max_length=500)


class BadgeRequestOut(BaseModel):
    id: int
    badge_type: BadgeType
    status: ClaimStatus
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BadgeRequestStatusOut(BaseModel):
    has_verified_badge: bool
    requests: list[BadgeRequestOut]


class BadgeRequestModerationItem(BaseModel):
    id: int
    badge_type: BadgeType
    status: ClaimStatus
    notes: str | None
    business_id: int
    business_name: str
    business_slug: str
    requester_name: str | None
    created_at: datetime


class BusinessModerationItem(BaseModel):
    id: int
    name: str
    slug: str
    city: str | None
    category_name: str | None
    business_type: BusinessType
    description: str | None
    created_at: datetime


class ClaimCreate(BaseModel):
    business_id: int
    notes: str | None = None


class ClaimSearchResult(BaseModel):
    id: int
    name: str
    slug: str
    city: str | None
    category_name: str | None
    is_claimed: bool


class ClaimOut(BaseModel):
    id: int
    business_id: int
    user_id: int
    status: ClaimStatus
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ClaimedBusinessSummary(BaseModel):
    id: int
    name: str
    slug: str


class ClaimSummary(BaseModel):
    id: int
    business_id: int
    business_name: str | None = None
    business_slug: str | None = None
    status: ClaimStatus
    notes: str | None
    created_at: datetime


class BusinessAccountOut(BaseModel):
    claimed_business: ClaimedBusinessSummary | None = None
    claims: list[ClaimSummary] = []


class FlagCreate(BaseModel):
    target_type: FlagTargetType
    target_id: int
    reason: str = Field(min_length=10)


class FlagOut(BaseModel):
    id: int
    target_type: FlagTargetType
    target_id: int
    reason: str
    status: FlagStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewResponseUpdate(BaseModel):
    response: str = Field(min_length=10)


class BusinessUpdate(BaseModel):
    description: str | None = None


class ModerationAction(BaseModel):
    action: str
    target_type: str
    target_id: int
    metadata: dict | None = None


class BadgeAssign(BaseModel):
    business_id: int
    badge_type: BadgeType


class BillingStatus(BaseModel):
    plan: str = "free"
    status: str = "active"
    message: str = "Billing is mocked in MVP. Stripe integration ready for production."
