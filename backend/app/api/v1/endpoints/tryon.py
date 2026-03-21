from fastapi import APIRouter, UploadFile, File
from app.schemas.tryon import TryOnResponse
from app.services.tryon_service import create_tryon_result

router = APIRouter()


@router.post("/tryon", response_model=TryOnResponse)
def tryon(
    person_file: UploadFile = File(...),
    cloth_file: UploadFile = File(...)
):
    result = create_tryon_result(
        person_file=person_file,
        cloth_file=cloth_file,
        use_remote=True
    )
    return TryOnResponse(**result)