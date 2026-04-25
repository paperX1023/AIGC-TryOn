from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import desc, select

from app.core.config import settings
from app.db.models import User, WardrobeItem
from app.db.session import is_database_enabled, optional_session_scope
from app.schemas.wardrobe import WardrobeDetectionResponse, WardrobeItemResponse
from app.utils.file_utils import save_upload_file, to_public_upload_url


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOTH_SOURCE_DIR = PROJECT_ROOT / "cloud_inference" / "gradio_demo" / "example" / "cloth"
DEFAULT_WARDROBE_UPLOAD_DIR = Path(settings.upload_dir) / "wardrobe" / "default"

DEFAULT_WARDROBE_ITEMS = [
    {"id": "default-04469", "filename": "04469_00.jpg", "name": "初始上衣 01", "category": "上衣"},
    {"id": "default-04743", "filename": "04743_00.jpg", "name": "初始上衣 02", "category": "上衣"},
    {"id": "default-09133", "filename": "09133_00.jpg", "name": "初始上衣 03", "category": "上衣"},
    {"id": "default-09163", "filename": "09163_00.jpg", "name": "初始上衣 04", "category": "上衣"},
    {"id": "default-09256", "filename": "09256_00.jpg", "name": "初始上衣 05", "category": "上衣"},
    {"id": "default-09305", "filename": "09305_00.jpg", "name": "初始上衣 06", "category": "上衣"},
]


def _read_image(file_path: str):
    image_bytes = np.fromfile(file_path, dtype=np.uint8)
    if image_bytes.size == 0:
        return None

    return cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)


def detect_clothing_image(file_path: str) -> WardrobeDetectionResponse:
    image = _read_image(file_path)
    if image is None:
        return WardrobeDetectionResponse(
            passed=False,
            score=0,
            message="服装图片检测失败：无法读取图片内容",
            checks={
                "可读取图片": False,
                "尺寸达标": False,
                "长宽比合理": False,
                "内容有效": False,
            },
        )

    height, width = image.shape[:2]
    aspect_ratio = height / width if width else 0
    content_std = float(np.std(image))
    checks = {
        "可读取图片": True,
        "尺寸达标": min(width, height) >= 128,
        "长宽比合理": 0.35 <= aspect_ratio <= 4.5,
        "内容有效": content_std >= 8,
    }
    passed_count = sum(1 for passed in checks.values() if passed)
    score = passed_count / len(checks)
    passed = all(checks.values())

    return WardrobeDetectionResponse(
        passed=passed,
        score=round(score, 2),
        message="服装图片检测通过，已加入服装库" if passed else "服装图片检测未通过，请上传清晰的单件服装图",
        checks=checks,
    )


def _ensure_default_wardrobe_files() -> list[WardrobeItemResponse]:
    DEFAULT_WARDROBE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    items: list[WardrobeItemResponse] = []

    for item in DEFAULT_WARDROBE_ITEMS:
        source_path = DEFAULT_CLOTH_SOURCE_DIR / item["filename"]
        if not source_path.exists():
            continue

        target_path = DEFAULT_WARDROBE_UPLOAD_DIR / item["filename"]
        if not target_path.exists():
            shutil.copy2(source_path, target_path)

        items.append(
            WardrobeItemResponse(
                id=item["id"],
                numeric_id=None,
                user_id=None,
                name=item["name"],
                category=item["category"],
                image_path=str(target_path),
                image_url=to_public_upload_url(str(target_path)),
                source="default",
                detection_result=None,
                created_at=None,
            )
        )

    return items


def _serialize_user_item(item: WardrobeItem) -> WardrobeItemResponse:
    return WardrobeItemResponse(
        id=f"user-{item.id}",
        numeric_id=item.id,
        user_id=item.user_id,
        name=item.name,
        category=item.category,
        image_path=item.image_path,
        image_url=item.image_url,
        source=item.source,
        detection_result=item.detection_result,
        created_at=item.created_at,
    )


def _require_user(db, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到用户 user_id={user_id}",
        )
    return user


def list_wardrobe_items(user_id: int | None = None) -> list[WardrobeItemResponse]:
    default_items = _ensure_default_wardrobe_files()
    if user_id is None or not is_database_enabled():
        return default_items

    with optional_session_scope() as db:
        if db is None:
            return default_items

        _require_user(db, user_id)
        user_items = db.scalars(
            select(WardrobeItem)
            .where(WardrobeItem.user_id == user_id)
            .order_by(desc(WardrobeItem.created_at))
        ).all()
        return [_serialize_user_item(item) for item in user_items] + default_items


def create_wardrobe_item_from_upload(
    *,
    upload_file: UploadFile,
    user_id: int | None,
    name: str | None = None,
    category: str | None = None,
) -> WardrobeItemResponse:
    sub_dir = f"wardrobe/user/{user_id}" if user_id is not None else "wardrobe/session"
    image_path = save_upload_file(upload_file, sub_dir=sub_dir)
    detection = detect_clothing_image(image_path)
    if not detection.passed:
        Path(image_path).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detection.message,
        )

    normalized_name = (name or "").strip() or "上传服装"
    normalized_category = (category or "").strip() or "上衣"
    image_url = to_public_upload_url(image_path)

    if user_id is None or not is_database_enabled():
        return WardrobeItemResponse(
            id=f"uploaded-{Path(image_path).stem}",
            numeric_id=None,
            user_id=user_id,
            name=normalized_name,
            category=normalized_category,
            image_path=image_path,
            image_url=image_url,
            source="uploaded",
            detection_result=detection,
            created_at=datetime.utcnow(),
        )

    with optional_session_scope() as db:
        if db is None:
            raise RuntimeError("数据库会话初始化失败")

        _require_user(db, user_id)
        item = WardrobeItem(
            user_id=user_id,
            name=normalized_name,
            category=normalized_category,
            image_path=image_path,
            image_url=image_url,
            detection_result=detection.model_dump(),
            source="user",
        )
        db.add(item)
        db.flush()
        db.refresh(item)
        return _serialize_user_item(item)


def resolve_wardrobe_item(item_id: str, user_id: int | None) -> WardrobeItemResponse:
    default_items = {item.id: item for item in _ensure_default_wardrobe_files()}
    if item_id in default_items:
        return default_items[item_id]

    if not item_id.startswith("user-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该服装库条目不能直接用于试穿，请重新上传服装图",
        )

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录后使用个人服装库")

    if not is_database_enabled():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="当前未配置数据库")

    try:
        numeric_id = int(item_id.removeprefix("user-"))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="服装库条目 ID 无效") from exc

    with optional_session_scope() as db:
        if db is None:
            raise RuntimeError("数据库会话初始化失败")

        item = db.get(WardrobeItem, numeric_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服装库条目不存在")
        if item.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不能使用其他用户的服装")
        if not Path(item.image_path).exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="服装图片文件不存在")

        return _serialize_user_item(item)
