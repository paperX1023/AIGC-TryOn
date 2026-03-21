from fastapi import APIRouter, UploadFile, File
from app.schemas.body import BodyAnalyzeResponse
from app.services.body_service import analyze_body_from_image

router = APIRouter()


@router.post("/analyze", response_model=BodyAnalyzeResponse)
def analyze_body(file: UploadFile = File(...)):
    result = analyze_body_from_image(file)
    return BodyAnalyzeResponse(**result)