import logging
from pathlib import Path
from urllib.parse import urljoin, urlparse
from uuid import uuid4

import requests
from fastapi import HTTPException, status

from app.core.config import settings
from app.services.persistence_service import save_tryon_record
from app.services.wardrobe_service import resolve_wardrobe_item
from app.utils.file_utils import save_upload_file, to_public_upload_url

logger = logging.getLogger(__name__)


def create_mock_tryon_result(person_file, cloth_file) -> dict:
    person_path = save_upload_file(person_file, sub_dir="tryon/person")
    cloth_path = save_upload_file(cloth_file, sub_dir="tryon/cloth")

    result_dir = Path("uploads") / "tryon" / "result"
    result_dir.mkdir(parents=True, exist_ok=True)

    result_path = person_path

    return {
        "record_id": None,
        "person_image_path": person_path,
        "person_image_url": to_public_upload_url(person_path),
        "cloth_image_path": cloth_path,
        "cloth_image_url": to_public_upload_url(cloth_path),
        "result_image_path": result_path,
        "result_image_url": to_public_upload_url(result_path),
        "status": "success",
        "message": "试穿接口已打通，当前返回的是占位结果，后续将接入真实 VTON 模型。",
    }


def call_remote_tryon_service(person_path: str, cloth_path: str) -> dict:
    if not settings.tryon_api_base_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="未配置 TRYON_API_BASE_URL，无法调用远程试穿服务"
        )

    url = f"{settings.tryon_api_base_url.rstrip('/')}/tryon"

    files = {
        "person_file": open(person_path, "rb"),
        "cloth_file": open(cloth_path, "rb"),
    }

    headers = {}
    if settings.tryon_api_key:
        headers["Authorization"] = f"Bearer {settings.tryon_api_key}"

    try:
        response = requests.post(url, files=files, headers=headers, timeout=120)
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"远程试穿服务请求失败: {str(e)}"
        )
    finally:
        files["person_file"].close()
        files["cloth_file"].close()

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"远程试穿服务返回异常: {response.status_code}, {response.text}"
        )

    try:
        remote_result = response.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="远程试穿服务返回的不是合法 JSON"
        )

    return remote_result


def _resolve_remote_result_url(remote_result: dict) -> str | None:
    explicit_url = str(remote_result.get("result_image_url", "")).strip()
    if explicit_url.startswith(("http://", "https://")):
        return explicit_url

    path_candidate = explicit_url or str(remote_result.get("result_image_path", "")).strip()
    if not path_candidate or not settings.tryon_api_base_url:
        return None

    return urljoin(f"{settings.tryon_api_base_url.rstrip('/')}/", path_candidate.lstrip("/"))


def _download_remote_result_image(remote_url: str) -> str | None:
    try:
        response = requests.get(remote_url, timeout=120)
        response.raise_for_status()
    except requests.RequestException:
        return None

    result_dir = Path(settings.upload_dir) / "tryon" / "result"
    result_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(urlparse(remote_url).path).suffix.lower() or ".jpg"
    local_path = result_dir / f"{uuid4().hex}{suffix}"
    local_path.write_bytes(response.content)
    return str(local_path)


def _finalize_result(
    *,
    result: dict,
    user_id: int | None,
    session_id: str | None,
    source: str,
) -> dict:
    result["record_id"] = save_tryon_record(
        user_id=user_id,
        session_code=session_id,
        tryon_result=result,
        source=source,
    )
    return result


def create_tryon_result(
    person_file,
    cloth_file=None,
    wardrobe_item_id: str | None = None,
    use_remote: bool = False,
    user_id: int | None = None,
    session_id: str | None = None,
) -> dict:
    if cloth_file is None and not wardrobe_item_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传服装图或选择服装库中的服装",
        )

    person_path = save_upload_file(person_file, sub_dir="tryon/person")
    if cloth_file is not None:
        cloth_path = save_upload_file(cloth_file, sub_dir="tryon/cloth")
        cloth_image_url = to_public_upload_url(cloth_path)
    else:
        wardrobe_item = resolve_wardrobe_item(wardrobe_item_id or "", user_id)
        cloth_path = wardrobe_item.image_path
        cloth_image_url = wardrobe_item.image_url

    if use_remote and settings.tryon_api_base_url:
        try:
            remote_result = call_remote_tryon_service(person_path, cloth_path)
            result_image_path = remote_result.get("result_image_path", person_path)
            remote_result_url = _resolve_remote_result_url(remote_result)
            downloaded_result_path = (
                _download_remote_result_image(remote_result_url) if remote_result_url else None
            )

            if downloaded_result_path:
                result_image_path = downloaded_result_path
                result_image_url = to_public_upload_url(downloaded_result_path)
            elif remote_result_url:
                result_image_url = remote_result_url
            elif str(result_image_path).startswith(("http://", "https://", "/uploads/")):
                result_image_url = str(result_image_path)
            else:
                result_image_url = to_public_upload_url(result_image_path)

            return _finalize_result(
                result={
                    "record_id": None,
                    "person_image_path": person_path,
                    "person_image_url": to_public_upload_url(person_path),
                    "cloth_image_path": cloth_path,
                    "cloth_image_url": cloth_image_url,
                    "result_image_path": result_image_path,
                    "result_image_url": result_image_url,
                    "status": remote_result.get("status", "success"),
                    "message": remote_result.get("message", "远程试穿成功"),
                },
                user_id=user_id,
                session_id=session_id,
                source="remote",
            )
        except HTTPException as exc:
            logger.warning("Remote try-on failed, fallback to mock result: %s", exc.detail)

    return _finalize_result(
        result={
            "record_id": None,
            "person_image_path": person_path,
            "person_image_url": to_public_upload_url(person_path),
            "cloth_image_path": cloth_path,
            "cloth_image_url": cloth_image_url,
            "result_image_path": person_path,
            "result_image_url": to_public_upload_url(person_path),
            "status": "success",
            "message": "当前未接入可用的远程试穿模型，已返回占位试穿结果。",
        },
        user_id=user_id,
        session_id=session_id,
        source="mock",
    )
