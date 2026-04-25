from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import get_optional_current_user, resolve_request_user_id
from app.schemas.tryon import TryOnResponse
from app.schemas.user import UserResponse
from app.services.tryon_service import create_tryon_result

router = APIRouter()


@router.post("/tryon", response_model=TryOnResponse)
def tryon(
    person_file: UploadFile = File(...),
    cloth_file: UploadFile | None = File(None),
    wardrobe_item_id: str | None = Form(None),
    user_id: int | None = Form(None),
    session_id: str | None = Form(None),
    current_user: UserResponse | None = Depends(get_optional_current_user),
):
    resolved_user_id = resolve_request_user_id(user_id, current_user)
    result = create_tryon_result(
        person_file=person_file,
        cloth_file=cloth_file,
        wardrobe_item_id=wardrobe_item_id,
        use_remote=True,
        user_id=resolved_user_id,
        session_id=session_id,
    )
    return TryOnResponse(**result)
