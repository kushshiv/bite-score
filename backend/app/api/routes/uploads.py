from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.evidence_upload import EvidenceUpload
from app.models.review import Review
from app.schemas import EvidenceOut
from app.services.storage import storage_service

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("", response_model=EvidenceOut)
async def upload_evidence(
    file: UploadFile = File(...),
    review_id: int | None = Form(None),
    business_id: int | None = Form(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not review_id and not business_id:
        raise HTTPException(status_code=400, detail="review_id or business_id required")

    if review_id:
        review = db.query(Review).filter(Review.id == review_id, Review.user_id == user.id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

    file_path, mime_type = await storage_service.save_image(file)
    upload = EvidenceUpload(
        review_id=review_id,
        business_id=business_id or (review.business_id if review_id else None),
        file_path=file_path,
        mime_type=mime_type,
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    return EvidenceOut(
        id=upload.id,
        file_url=f"{settings.api_base_url}/uploads/{file_path.split('/')[-1]}",
        mime_type=upload.mime_type,
        verified=upload.verified,
        created_at=upload.created_at,
    )


@router.patch("/{upload_id}/verify", response_model=EvidenceOut)
def verify_upload(
    upload_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.MODERATOR, UserRole.ADMIN)),
):
    upload = db.query(EvidenceUpload).filter(EvidenceUpload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    upload.verified = True
    db.commit()
    db.refresh(upload)
    return EvidenceOut(
        id=upload.id,
        file_url=f"{settings.api_base_url}/uploads/{upload.file_path.split('/')[-1]}",
        mime_type=upload.mime_type,
        verified=upload.verified,
        created_at=upload.created_at,
    )
