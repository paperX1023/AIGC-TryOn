from fastapi import APIRouter

from app.schemas.chat import ChatRecommendRequest, ChatRecommendResponse
from app.services.chat_service import generate_chat_recommendation

router = APIRouter()


@router.post("/recommend", response_model=ChatRecommendResponse)
def recommend_chat(data: ChatRecommendRequest):
    result = generate_chat_recommendation(data)
    return ChatRecommendResponse(**result)
