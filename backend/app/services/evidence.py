from app.config import settings


def evidence_file_url(file_path: str) -> str:
    return f"{settings.api_base_url}/uploads/{file_path.split('/')[-1]}"
