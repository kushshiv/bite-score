import enum


class UserRole(str, enum.Enum):
    USER = "user"
    MODERATOR = "moderator"
    BUSINESS_OWNER = "business_owner"
    ADMIN = "admin"


class BusinessType(str, enum.Enum):
    RESTAURANT = "restaurant"
    STREET_VENDOR = "street_vendor"
    CAFE = "cafe"
    FOOD_COURT = "food_court"
    BAKERY = "bakery"
    CLOUD_KITCHEN = "cloud_kitchen"
    OTHER = "other"


class BusinessStatus(str, enum.Enum):
    ACTIVE = "active"
    UNDER_REVIEW = "under_review"
    HIDDEN = "hidden"


class VisitType(str, enum.Enum):
    DINE_IN = "dine_in"
    TAKEAWAY = "takeaway"
    DELIVERY = "delivery"


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    HIDDEN = "hidden"
    FLAGGED = "flagged"


class ClaimStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class BadgeType(str, enum.Enum):
    CLAIMED = "claimed"
    VERIFIED = "verified"
    HIGH_CONFIDENCE = "high_confidence"
    UNDER_REVIEW = "under_review"


class FlagTargetType(str, enum.Enum):
    REVIEW = "review"
    BUSINESS = "business"
    EVIDENCE = "evidence"


class FlagStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class CertificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
