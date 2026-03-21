from pathlib import Path
import requests
from fastapi import HTTPException, status

from app.core.config import settings
from app.utils.file_utils import save_upload_file, to_public_upload_url


def create_mock_tryon_result(person_file, cloth_file) -> dict:
    person_path = save_upload_file(person_file, sub_dir="tryon/person")
    cloth_path = save_upload_file(cloth_file, sub_dir="tryon/cloth")

    result_dir = Path("uploads") / "tryon" / "result"
    result_dir.mkdir(parents=True, exist_ok=True)

    result_path = person_path

    return {
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


def create_tryon_result(person_file, cloth_file, use_remote: bool = False) -> dict:
    person_path = save_upload_file(person_file, sub_dir="tryon/person")
    cloth_path = save_upload_file(cloth_file, sub_dir="tryon/cloth")

    if use_remote and settings.tryon_api_base_url:
        try:
            remote_result = call_remote_tryon_service(person_path, cloth_path)
            result_image_path = remote_result.get("result_image_path", person_path)
            result_image_url = (
                result_image_path
                if str(result_image_path).startswith(("http://", "https://", "/uploads/"))
                else to_public_upload_url(result_image_path)
            )

            return {
                "person_image_path": person_path,
                "person_image_url": to_public_upload_url(person_path),
                "cloth_image_path": cloth_path,
                "cloth_image_url": to_public_upload_url(cloth_path),
                "result_image_path": result_image_path,
                "result_image_url": result_image_url,
                "status": remote_result.get("status", "success"),
                "message": remote_result.get("message", "远程试穿成功"),
            }
        except HTTPException as e:
            print("Remote try-on failed, fallback to mock result:", e.detail)

    return {
        "person_image_path": person_path,
        "person_image_url": to_public_upload_url(person_path),
        "cloth_image_path": cloth_path,
        "cloth_image_url": to_public_upload_url(cloth_path),
        "result_image_path": person_path,
        "result_image_url": to_public_upload_url(person_path),
        "status": "success",
        "message": "当前未接入可用的远程试穿模型，已返回占位试穿结果。",
    }
