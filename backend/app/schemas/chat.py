from typing import Optional

from pydantic import BaseModel

from app.schemas.recommend import RecommendResult
from app.schemas.style import StyleParsedResult


class ChatBodyContext(BaseModel):
    gender: str = "未知"
    body_shape: str
    shoulder_type: str
    waist_type: str
    leg_ratio: str
    analysis_summary: Optional[str] = None


class ChatRecommendRequest(BaseModel):
    text: str
    session_id: Optional[str] = None
    body_context: Optional[ChatBodyContext] = None


class ChatRecommendResponse(BaseModel):
    reply: str
    session_id: str
    parsed_result: StyleParsedResult
    recommend_result: Optional[RecommendResult] = None
