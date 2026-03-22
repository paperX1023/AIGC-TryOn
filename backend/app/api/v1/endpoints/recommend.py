from fastapi import APIRouter
from app.schemas.recommend import RecommendRequest, RecommendResponse
from app.services.recommend_service import generate_recommendation

router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
def recommend(data: RecommendRequest):
    result = generate_recommendation(data, use_llm_reason=True)

    return RecommendResponse(
        input_summary={
            "gender": data.gender,
            "body_shape": data.body_shape,
            "shoulder_type": data.shoulder_type,
            "waist_type": data.waist_type,
            "leg_ratio": data.leg_ratio,
            "styles": data.styles,
            "scene": data.scene,
            "goals": data.goals
        },
        recommend_result=result
    )
