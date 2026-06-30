import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from sqlalchemy.orm import Session, joinedload

from app.models.business import Business
from app.models.location import Location

BLOCK_SIMILARITY = 0.90
FLAG_SIMILARITY = 0.75


@dataclass(frozen=True)
class SimilarBusiness:
    id: int
    name: str
    slug: str
    similarity: float
    match_type: str  # exact | high | medium


@dataclass(frozen=True)
class DuplicateCheckResult:
    matches: list[SimilarBusiness]
    block: bool
    requires_acknowledgement: bool

    @property
    def has_similar(self) -> bool:
        return bool(self.matches)


def normalize_business_name(name: str) -> str:
    lowered = name.lower()
    cleaned = re.sub(r"[^a-z0-9]+", " ", lowered)
    return " ".join(cleaned.split())


def name_similarity(left: str, right: str) -> float:
    normalized_left = normalize_business_name(left)
    normalized_right = normalize_business_name(right)
    if not normalized_left or not normalized_right:
        return 0.0
    if normalized_left == normalized_right:
        return 1.0
    return SequenceMatcher(None, normalized_left, normalized_right).ratio()


def _match_type(similarity: float) -> str:
    if similarity >= BLOCK_SIMILARITY:
        return "high"
    if similarity >= FLAG_SIMILARITY:
        return "medium"
    return "low"


def find_similar_businesses(db: Session, name: str, city: str) -> list[SimilarBusiness]:
    city_key = city.strip()
    businesses = (
        db.query(Business)
        .options(joinedload(Business.location))
        .join(Location)
        .filter(Location.city.ilike(city_key))
        .all()
    )

    matches: list[SimilarBusiness] = []
    for business in businesses:
        similarity = name_similarity(name, business.name)
        if similarity < FLAG_SIMILARITY:
            continue
        match_type = "exact" if similarity == 1.0 else _match_type(similarity)
        matches.append(
            SimilarBusiness(
                id=business.id,
                name=business.name,
                slug=business.slug,
                similarity=round(similarity, 3),
                match_type=match_type,
            )
        )

    matches.sort(key=lambda item: item.similarity, reverse=True)
    return matches


def check_duplicates(db: Session, name: str, city: str) -> DuplicateCheckResult:
    matches = find_similar_businesses(db, name, city)
    if not matches:
        return DuplicateCheckResult(matches=[], block=False, requires_acknowledgement=False)

    top = matches[0]
    if top.match_type == "exact" or top.similarity >= BLOCK_SIMILARITY:
        return DuplicateCheckResult(matches=matches, block=True, requires_acknowledgement=False)

    return DuplicateCheckResult(
        matches=matches,
        block=False,
        requires_acknowledgement=True,
    )
