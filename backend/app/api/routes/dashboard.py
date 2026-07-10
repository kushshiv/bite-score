from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.admin_audit import AdminAudit
from app.models.badge_request import BadgeRequest
from app.models.business import Business
from app.models.certification_upload import CertificationUpload
from app.models.claim_request import ClaimRequest
from app.models.enums import (
    BadgeType,
    BusinessStatus,
    CertificationStatus,
    ClaimStatus,
    FlagStatus,
    ReviewStatus,
    UserRole,
)
from app.models.evidence_upload import EvidenceUpload
from app.models.report_flag import ReportFlag
from app.models.review import Review
from app.models.user import User
from app.models.verification_badge import VerificationBadge
from app.schemas import (
    BadgeAssign,
    BadgeRequestCreate,
    BadgeRequestModerationItem,
    BadgeRequestOut,
    BadgeRequestStatusOut,
    BusinessAccountOut,
    BusinessModerationItem,
    BusinessUpdate,
    CertificationListOut,
    CertificationModerationItem,
    CertificationOut,
    ClaimCreate,
    ClaimedBusinessSummary,
    ClaimOut,
    ClaimSearchResult,
    ClaimSummary,
    EvidenceModerationItem,
    FlagCreate,
    FlagOut,
    ModerationAction,
    ReviewModerationItem,
    ReviewResponseUpdate,
    ScoreBreakdown,
    ScoreTrendOut,
)
from app.services.business_query import build_business_query
from app.services.evidence import evidence_file_url
from app.services.scoring import compute_business_score, compute_business_score_trend
from app.services.storage import storage_service

router = APIRouter(tags=["dashboard"])


def _require_claimed_business(db: Session, user: User) -> Business:
    business = db.query(Business).filter(Business.claimed_by_id == user.id).first()
    if not business:
        raise HTTPException(status_code=404, detail="No claimed business found")
    return business


def _certification_out(cert: CertificationUpload) -> CertificationOut:
    return CertificationOut(
        id=cert.id,
        title=cert.title,
        file_url=evidence_file_url(cert.file_path),
        mime_type=cert.mime_type,
        status=cert.status,
        created_at=cert.created_at,
    )


def _business_has_badge(db: Session, business_id: int, badge_type: BadgeType) -> bool:
    return (
        db.query(VerificationBadge)
        .filter(
            VerificationBadge.business_id == business_id,
            VerificationBadge.badge_type == badge_type,
        )
        .first()
        is not None
    )


def _issue_badge_if_missing(
    db: Session, business_id: int, badge_type: BadgeType, issued_by_id: int
) -> VerificationBadge | None:
    existing = (
        db.query(VerificationBadge)
        .filter(
            VerificationBadge.business_id == business_id,
            VerificationBadge.badge_type == badge_type,
        )
        .first()
    )
    if existing:
        return None
    badge = VerificationBadge(
        business_id=business_id, badge_type=badge_type, issued_by_id=issued_by_id
    )
    db.add(badge)
    return badge


def _grant_verified_badge_for_business(db: Session, business_id: int, issued_by_id: int) -> None:
    _issue_badge_if_missing(db, business_id, BadgeType.VERIFIED, issued_by_id)
    pending_requests = (
        db.query(BadgeRequest)
        .filter(
            BadgeRequest.business_id == business_id,
            BadgeRequest.badge_type == BadgeType.VERIFIED,
            BadgeRequest.status == ClaimStatus.PENDING,
        )
        .all()
    )
    for request in pending_requests:
        request.status = ClaimStatus.APPROVED


@router.post("/claims", response_model=ClaimOut)
def create_claim(
    data: ClaimCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role in (UserRole.MODERATOR, UserRole.ADMIN):
        raise HTTPException(
            status_code=403,
            detail="Moderator and admin accounts cannot submit business claims",
        )
    if user.role != UserRole.BUSINESS_OWNER:
        raise HTTPException(
            status_code=403,
            detail="Only business owner accounts can submit claims",
        )

    if db.query(Business).filter(Business.claimed_by_id == user.id).first():
        raise HTTPException(status_code=400, detail="You already manage a claimed business")

    business = db.query(Business).filter(Business.id == data.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if business.claimed_by_id:
        raise HTTPException(status_code=400, detail="Business already claimed")

    pending = (
        db.query(ClaimRequest)
        .filter(
            ClaimRequest.user_id == user.id,
            ClaimRequest.business_id == data.business_id,
            ClaimRequest.status == ClaimStatus.PENDING,
        )
        .first()
    )
    if pending:
        raise HTTPException(
            status_code=400, detail="You already have a pending claim for this business"
        )

    claim = ClaimRequest(business_id=data.business_id, user_id=user.id, notes=data.notes)
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


@router.get("/business-dashboard/claim-search", response_model=list[ClaimSearchResult])
def search_businesses_to_claim(
    q: str = Query(..., min_length=2),
    city: str | None = None,
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != UserRole.BUSINESS_OWNER:
        raise HTTPException(
            status_code=403,
            detail="Only business owner accounts can search to claim",
        )

    businesses = build_business_query(db, q=q, city=city).limit(limit).all()
    return [
        ClaimSearchResult(
            id=business.id,
            name=business.name,
            slug=business.slug,
            city=business.location.city if business.location else None,
            category_name=business.category.name if business.category else None,
            is_claimed=bool(business.claimed_by_id),
        )
        for business in businesses
    ]


@router.get("/dashboard/claims", response_model=list[ClaimOut])
def my_claims(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(ClaimRequest).filter(ClaimRequest.user_id == user.id).all()


@router.get("/business-dashboard/account", response_model=BusinessAccountOut)
def business_account(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    claimed = db.query(Business).filter(Business.claimed_by_id == user.id).first()
    claims = (
        db.query(ClaimRequest)
        .options(joinedload(ClaimRequest.business))
        .filter(ClaimRequest.user_id == user.id)
        .order_by(ClaimRequest.created_at.desc())
        .all()
    )

    claimed_business = None
    if claimed:
        claimed_business = ClaimedBusinessSummary(
            id=claimed.id, name=claimed.name, slug=claimed.slug
        )

    return BusinessAccountOut(
        claimed_business=claimed_business,
        claims=[
            ClaimSummary(
                id=claim.id,
                business_id=claim.business_id,
                business_name=claim.business.name if claim.business else None,
                business_slug=claim.business.slug if claim.business else None,
                status=claim.status,
                notes=claim.notes,
                created_at=claim.created_at,
            )
            for claim in claims
        ],
    )


@router.get("/business-dashboard/stats")
def business_dashboard_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    business = db.query(Business).filter(Business.claimed_by_id == user.id).first()
    if not business:
        raise HTTPException(status_code=404, detail="No claimed business found")
    score = compute_business_score(db, business.id)
    reviews = db.query(Review).filter(Review.business_id == business.id).count()
    return {
        "business": {"id": business.id, "name": business.name, "slug": business.slug},
        "score": ScoreBreakdown(**score),
        "total_reviews": reviews,
    }


@router.get("/business-dashboard/score-trend", response_model=ScoreTrendOut)
def business_score_trend(
    weeks: int = Query(12, ge=4, le=52),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    business = db.query(Business).filter(Business.claimed_by_id == user.id).first()
    if not business:
        raise HTTPException(status_code=404, detail="No claimed business found")

    points = compute_business_score_trend(db, business.id, weeks=weeks)
    return ScoreTrendOut(points=points, weeks=weeks)


@router.patch("/business-dashboard/profile")
def update_business_profile(
    data: BusinessUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    business = db.query(Business).filter(Business.claimed_by_id == user.id).first()
    if not business:
        raise HTTPException(status_code=404, detail="No claimed business found")
    if data.description is not None:
        business.description = data.description
    db.commit()
    return {"message": "Profile updated"}


@router.patch("/business-dashboard/reviews/{review_id}/respond")
def respond_to_review(
    review_id: int,
    data: ReviewResponseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    business = db.query(Business).filter(Business.claimed_by_id == user.id).first()
    if not business:
        raise HTTPException(status_code=404, detail="No claimed business found")
    review = (
        db.query(Review).filter(Review.id == review_id, Review.business_id == business.id).first()
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.business_response = data.response
    db.commit()
    return {"message": "Response posted"}


@router.get("/business-dashboard/certifications", response_model=CertificationListOut)
def list_certifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    business = _require_claimed_business(db, user)
    certs = (
        db.query(CertificationUpload)
        .filter(CertificationUpload.business_id == business.id)
        .order_by(CertificationUpload.created_at.desc())
        .all()
    )
    return CertificationListOut(
        has_verified_badge=_business_has_badge(db, business.id, BadgeType.VERIFIED),
        certifications=[_certification_out(cert) for cert in certs],
    )


@router.post("/business-dashboard/certifications", response_model=CertificationOut)
async def upload_certification(
    file: UploadFile = File(...),
    title: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    business = _require_claimed_business(db, user)
    trimmed_title = title.strip()
    if len(trimmed_title) < 3:
        raise HTTPException(status_code=400, detail="Title must be at least 3 characters")

    file_path, mime_type = await storage_service.save_document(file)
    cert = CertificationUpload(
        business_id=business.id,
        uploaded_by_id=user.id,
        title=trimmed_title,
        file_path=file_path,
        mime_type=mime_type,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return _certification_out(cert)


@router.get("/business-dashboard/badge-requests", response_model=BadgeRequestStatusOut)
def list_badge_requests(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    business = _require_claimed_business(db, user)
    requests = (
        db.query(BadgeRequest)
        .filter(BadgeRequest.business_id == business.id)
        .order_by(BadgeRequest.created_at.desc())
        .all()
    )
    return BadgeRequestStatusOut(
        has_verified_badge=_business_has_badge(db, business.id, BadgeType.VERIFIED),
        requests=[BadgeRequestOut.model_validate(req) for req in requests],
    )


@router.post("/business-dashboard/badge-requests", response_model=BadgeRequestOut)
def request_verified_badge(
    data: BadgeRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    business = _require_claimed_business(db, user)
    if _business_has_badge(db, business.id, BadgeType.VERIFIED):
        raise HTTPException(status_code=400, detail="Your business already has the verified badge")

    pending = (
        db.query(BadgeRequest)
        .filter(
            BadgeRequest.business_id == business.id,
            BadgeRequest.badge_type == BadgeType.VERIFIED,
            BadgeRequest.status == ClaimStatus.PENDING,
        )
        .first()
    )
    if pending:
        raise HTTPException(
            status_code=400, detail="You already have a pending verified badge request"
        )

    request = BadgeRequest(
        business_id=business.id,
        user_id=user.id,
        badge_type=BadgeType.VERIFIED,
        notes=data.notes.strip() if data.notes else None,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.post("/flags", response_model=FlagOut)
def create_flag(
    data: FlagCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    flag = ReportFlag(
        reporter_id=user.id,
        target_type=data.target_type,
        target_id=data.target_id,
        reason=data.reason,
    )
    db.add(flag)
    db.commit()
    db.refresh(flag)
    return flag


@router.get("/admin/moderation-queue")
def moderation_queue(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.MODERATOR, UserRole.ADMIN)),
):
    pending_reviews = (
        db.query(Review)
        .options(
            joinedload(Review.structured_score),
            joinedload(Review.user),
            joinedload(Review.business),
        )
        .filter(Review.status == ReviewStatus.PENDING)
        .order_by(Review.created_at.desc())
        .limit(50)
        .all()
    )
    open_flags = db.query(ReportFlag).filter(ReportFlag.status == FlagStatus.OPEN).limit(50).all()
    pending_claims = (
        db.query(ClaimRequest).filter(ClaimRequest.status == ClaimStatus.PENDING).limit(50).all()
    )
    unverified_evidence = (
        db.query(EvidenceUpload)
        .options(joinedload(EvidenceUpload.business))
        .filter(EvidenceUpload.verified.is_(False))
        .order_by(EvidenceUpload.created_at.asc())
        .limit(50)
        .all()
    )
    evidence_items = [
        EvidenceModerationItem(
            id=upload.id,
            file_url=evidence_file_url(upload.file_path),
            mime_type=upload.mime_type,
            verified=upload.verified,
            review_id=upload.review_id,
            business_id=upload.business_id,
            business_name=upload.business.name if upload.business else None,
            business_slug=upload.business.slug if upload.business else None,
            created_at=upload.created_at,
        )
        for upload in unverified_evidence
    ]
    pending_certifications = (
        db.query(CertificationUpload)
        .options(joinedload(CertificationUpload.business))
        .filter(CertificationUpload.status == CertificationStatus.PENDING)
        .order_by(CertificationUpload.created_at.asc())
        .limit(50)
        .all()
    )
    certification_items = [
        CertificationModerationItem(
            id=cert.id,
            title=cert.title,
            file_url=evidence_file_url(cert.file_path),
            mime_type=cert.mime_type,
            status=cert.status,
            business_id=cert.business_id,
            business_name=cert.business.name,
            business_slug=cert.business.slug,
            created_at=cert.created_at,
        )
        for cert in pending_certifications
    ]
    pending_badge_requests = (
        db.query(BadgeRequest)
        .options(joinedload(BadgeRequest.business), joinedload(BadgeRequest.user))
        .filter(
            BadgeRequest.status == ClaimStatus.PENDING,
            BadgeRequest.badge_type == BadgeType.VERIFIED,
        )
        .order_by(BadgeRequest.created_at.asc())
        .limit(50)
        .all()
    )
    badge_request_items = [
        BadgeRequestModerationItem(
            id=req.id,
            badge_type=req.badge_type,
            status=req.status,
            notes=req.notes,
            business_id=req.business_id,
            business_name=req.business.name,
            business_slug=req.business.slug,
            requester_name=req.user.full_name,
            created_at=req.created_at,
        )
        for req in pending_badge_requests
    ]
    pending_businesses = (
        db.query(Business)
        .options(joinedload(Business.category), joinedload(Business.location))
        .filter(Business.status == BusinessStatus.UNDER_REVIEW)
        .order_by(Business.created_at.asc())
        .limit(50)
        .all()
    )
    business_items = [
        BusinessModerationItem(
            id=business.id,
            name=business.name,
            slug=business.slug,
            city=business.location.city if business.location else None,
            category_name=business.category.name if business.category else None,
            business_type=business.business_type,
            description=business.description,
            created_at=business.created_at,
        )
        for business in pending_businesses
    ]
    review_items = [
        ReviewModerationItem(
            id=review.id,
            business_id=review.business_id,
            business_name=review.business.name,
            business_slug=review.business.slug,
            visit_type=review.visit_type,
            visit_date=review.visit_date,
            notes=review.notes,
            reviewer_name=review.user.full_name,
            oil_freshness_concern=(
                review.structured_score.oil_freshness_concern if review.structured_score else False
            ),
            created_at=review.created_at,
        )
        for review in pending_reviews
    ]
    return {
        "pending_reviews": len(review_items),
        "pending_evidence": len(evidence_items),
        "pending_certifications": len(certification_items),
        "pending_badge_requests": len(badge_request_items),
        "pending_businesses": len(business_items),
        "reviews": review_items,
        "open_flags": [
            {"id": f.id, "target_type": f.target_type, "reason": f.reason} for f in open_flags
        ],
        "pending_claims": [{"id": c.id, "business_id": c.business_id} for c in pending_claims],
        "evidence": evidence_items,
        "certifications": certification_items,
        "badge_requests": badge_request_items,
        "businesses": business_items,
    }


@router.post("/admin/moderate")
def moderate(
    data: ModerationAction,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.MODERATOR, UserRole.ADMIN)),
):
    if data.target_type == "review":
        review = db.query(Review).filter(Review.id == data.target_id).first()
        if review:
            if data.action == "approve":
                review.status = ReviewStatus.APPROVED
            elif data.action == "hide":
                review.status = ReviewStatus.HIDDEN
            elif data.action == "flag":
                review.status = ReviewStatus.FLAGGED

    elif data.target_type == "claim":
        claim = db.query(ClaimRequest).filter(ClaimRequest.id == data.target_id).first()
        if claim:
            if data.action == "approve":
                claim.status = ClaimStatus.APPROVED
                business = db.query(Business).filter(Business.id == claim.business_id).first()
                if business:
                    business.claimed_by_id = claim.user_id
                    badge = VerificationBadge(
                        business_id=business.id, badge_type=BadgeType.CLAIMED, issued_by_id=user.id
                    )
                    db.add(badge)
            elif data.action == "reject":
                claim.status = ClaimStatus.REJECTED

    elif data.target_type == "flag":
        flag = db.query(ReportFlag).filter(ReportFlag.id == data.target_id).first()
        if flag:
            flag.status = FlagStatus.RESOLVED if data.action == "resolve" else FlagStatus.DISMISSED

    elif data.target_type == "certification":
        cert = (
            db.query(CertificationUpload).filter(CertificationUpload.id == data.target_id).first()
        )
        if cert:
            if data.action == "approve":
                cert.status = CertificationStatus.VERIFIED
                _grant_verified_badge_for_business(db, cert.business_id, user.id)
            elif data.action == "reject":
                cert.status = CertificationStatus.REJECTED

    elif data.target_type == "badge_request":
        badge_request = db.query(BadgeRequest).filter(BadgeRequest.id == data.target_id).first()
        if badge_request:
            if data.action == "approve":
                badge_request.status = ClaimStatus.APPROVED
                _issue_badge_if_missing(
                    db,
                    badge_request.business_id,
                    badge_request.badge_type,
                    user.id,
                )
            elif data.action == "reject":
                badge_request.status = ClaimStatus.REJECTED

    elif data.target_type == "business":
        business = db.query(Business).filter(Business.id == data.target_id).first()
        if business:
            if data.action == "approve":
                business.status = BusinessStatus.ACTIVE
            elif data.action == "reject":
                business.status = BusinessStatus.HIDDEN

    audit = AdminAudit(
        actor_id=user.id,
        action=data.action,
        target_type=data.target_type,
        target_id=data.target_id,
        metadata_json=data.metadata,
    )
    db.add(audit)
    db.commit()
    return {"message": "Action recorded"}


@router.post("/admin/badges")
def assign_badge(
    data: BadgeAssign,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN)),
):
    if _business_has_badge(db, data.business_id, data.badge_type):
        raise HTTPException(status_code=400, detail="Badge already assigned")
    _issue_badge_if_missing(db, data.business_id, data.badge_type, user.id)
    db.add(
        AdminAudit(
            actor_id=user.id,
            action="assign_badge",
            target_type="business",
            target_id=data.business_id,
            metadata_json={"badge_type": data.badge_type.value},
        )
    )
    db.commit()
    return {"message": "Badge assigned"}


@router.get("/admin/audits")
def list_audits(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN)),
):
    audits = db.query(AdminAudit).order_by(AdminAudit.created_at.desc()).limit(100).all()
    return [
        {
            "id": a.id,
            "action": a.action,
            "target_type": a.target_type,
            "target_id": a.target_id,
            "metadata": a.metadata_json,
            "created_at": a.created_at,
        }
        for a in audits
    ]
