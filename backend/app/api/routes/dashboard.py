from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.admin_audit import AdminAudit
from app.models.business import Business
from app.models.claim_request import ClaimRequest
from app.models.enums import BadgeType, ClaimStatus, FlagStatus, ReviewStatus, UserRole
from app.models.evidence_upload import EvidenceUpload
from app.models.report_flag import ReportFlag
from app.models.review import Review
from app.models.user import User
from app.models.verification_badge import VerificationBadge
from app.schemas import (
    BadgeAssign,
    BusinessUpdate,
    ClaimCreate,
    ClaimOut,
    EvidenceModerationItem,
    FlagCreate,
    FlagOut,
    ModerationAction,
    ReviewResponseUpdate,
    ScoreBreakdown,
)
from app.services.evidence import evidence_file_url
from app.services.scoring import compute_business_score

router = APIRouter(tags=["dashboard"])


@router.post("/claims", response_model=ClaimOut)
def create_claim(
    data: ClaimCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    business = db.query(Business).filter(Business.id == data.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if business.claimed_by_id:
        raise HTTPException(status_code=400, detail="Business already claimed")

    claim = ClaimRequest(business_id=data.business_id, user_id=user.id, notes=data.notes)
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


@router.get("/dashboard/claims", response_model=list[ClaimOut])
def my_claims(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(ClaimRequest).filter(ClaimRequest.user_id == user.id).all()


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
        .options(joinedload(Review.structured_score), joinedload(Review.user))
        .filter(Review.status == ReviewStatus.PENDING)
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
    return {
        "pending_reviews": len(pending_reviews),
        "pending_evidence": len(evidence_items),
        "reviews": [
            {"id": r.id, "business_id": r.business_id, "notes": r.notes} for r in pending_reviews
        ],
        "open_flags": [
            {"id": f.id, "target_type": f.target_type, "reason": f.reason} for f in open_flags
        ],
        "pending_claims": [{"id": c.id, "business_id": c.business_id} for c in pending_claims],
        "evidence": evidence_items,
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
    existing = (
        db.query(VerificationBadge)
        .filter(
            VerificationBadge.business_id == data.business_id,
            VerificationBadge.badge_type == data.badge_type,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Badge already assigned")
    badge = VerificationBadge(
        business_id=data.business_id, badge_type=data.badge_type, issued_by_id=user.id
    )
    db.add(badge)
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
