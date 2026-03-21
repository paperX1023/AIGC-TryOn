from fastapi import APIRouter
from app.schemas.style import StyleParseRequest, StyleParseResponse
from app.services.style_service import parse_style_text

router = APIRouter()


@router.post("/parse", response_model=StyleParseResponse)
def parse_style(data: StyleParseRequest):
    result = parse_style_text(data.text, use_llm=True)

    return StyleParseResponse(
        raw_text=data.text,
        parsed_result=result
    )