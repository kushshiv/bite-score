import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image

from app.config import settings

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
DOCUMENT_TYPES = ALLOWED_TYPES | {"application/pdf"}
MAX_SIZE = 5 * 1024 * 1024
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024


class StorageService:
    def __init__(self) -> None:
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_image(self, file: UploadFile) -> tuple[str, str]:
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400, detail="Only JPEG, PNG, and WebP images are allowed"
            )

        content = await file.read()
        if len(content) > MAX_SIZE:
            raise HTTPException(status_code=400, detail="File too large (max 5MB)")

        try:
            Image.open(__import__("io").BytesIO(content)).verify()
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid image file") from exc

        ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
        filename = f"{uuid.uuid4().hex}.{ext}"
        path = self.upload_dir / filename
        path.write_bytes(content)
        return str(path), file.content_type or "image/jpeg"

    async def save_document(self, file: UploadFile) -> tuple[str, str]:
        content_type = file.content_type or ""
        if content_type not in DOCUMENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only JPEG, PNG, WebP images and PDF documents are allowed",
            )

        content = await file.read()
        max_size = MAX_DOCUMENT_SIZE if content_type == "application/pdf" else MAX_SIZE
        if len(content) > max_size:
            limit = "10MB" if content_type == "application/pdf" else "5MB"
            raise HTTPException(status_code=400, detail=f"File too large (max {limit})")

        if content_type == "application/pdf":
            if not content.startswith(b"%PDF"):
                raise HTTPException(status_code=400, detail="Invalid PDF file")
        else:
            try:
                Image.open(__import__("io").BytesIO(content)).verify()
            except Exception as exc:
                raise HTTPException(status_code=400, detail="Invalid image file") from exc

        ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "bin"
        filename = f"{uuid.uuid4().hex}.{ext}"
        path = self.upload_dir / filename
        path.write_bytes(content)
        return str(path), content_type


storage_service = StorageService()
