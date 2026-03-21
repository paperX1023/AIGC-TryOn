from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]


def save_upload_file(upload_file: UploadFile, sub_dir: str = "body") -> str:
    if upload_file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"只能上传图片格式 (支持: jpg, png, webp)，你上传的是: {upload_file.content_type}"
        )

    target_dir = UPLOAD_DIR / sub_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    file_suffix = Path(upload_file.filename).suffix.lower() if upload_file.filename else ".jpg"
    new_file_name = f"{uuid4().hex}{file_suffix}"
    file_path = target_dir / new_file_name

    file_bytes = upload_file.file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="上传文件不能为空"
        )

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return str(file_path)


def to_public_upload_url(file_path: str) -> str:
    normalized_path = Path(file_path)
    parts = list(normalized_path.parts)

    if "uploads" in parts:
        upload_index = parts.index("uploads")
        relative_parts = parts[upload_index + 1:]
    else:
        relative_parts = parts

    relative_url = "/".join(relative_parts)
    return f"/uploads/{relative_url}"
