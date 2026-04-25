from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import get_optional_current_user, resolve_request_user_id
from app.schemas.body import BodyAnalyzeResponse
from app.schemas.user import UserResponse
from app.services.body_service import analyze_body_from_image

router = APIRouter()


@router.post("/analyze", response_model=BodyAnalyzeResponse)
def analyze_body(
    file: UploadFile = File(...),
    user_id: int | None = Form(None),
    current_user: UserResponse | None = Depends(get_optional_current_user),
):
    result = analyze_body_from_image(
        file,
        user_id=resolve_request_user_id(user_id, current_user),
    )
    return BodyAnalyzeResponse(**result)
