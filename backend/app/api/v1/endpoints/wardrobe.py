from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.api.deps import get_optional_current_user, resolve_request_user_id
from app.schemas.user import UserResponse
from app.schemas.wardrobe import WardrobeItemResponse, WardrobeListResponse
from app.services.wardrobe_service import create_wardrobe_item_from_upload, list_wardrobe_items

router = APIRouter()


@router.get("/wardrobe", response_model=WardrobeListResponse)
def list_wardrobe_endpoint(
    user_id: int | None = Query(None),
    current_user: UserResponse | None = Depends(get_optional_current_user),
):
    resolved_user_id = resolve_request_user_id(user_id, current_user)
    return WardrobeListResponse(items=list_wardrobe_items(resolved_user_id))


@router.post("/wardrobe/upload", response_model=WardrobeItemResponse)
def upload_wardrobe_item_endpoint(
    cloth_file: UploadFile = File(...),
    user_id: int | None = Form(None),
    name: str | None = Form(None),
    category: str | None = Form(None),
    current_user: UserResponse | None = Depends(get_optional_current_user),
):
    resolved_user_id = resolve_request_user_id(user_id, current_user)
    return create_wardrobe_item_from_upload(
        upload_file=cloth_file,
        user_id=resolved_user_id,
        name=name,
        category=category,
    )
