from typing import Optional

from pydantic import BaseModel

from app.schemas.recommend import RecommendResult
from app.schemas.style import StyleParsedResult
from app.schemas.taxonomy import BodyShape, Gender, LegRatio, ShoulderType, WaistType


class ChatBodyContext(BaseModel):
    gender: Gender = Gender.UNKNOWN
    body_shape: BodyShape
    shoulder_type: ShoulderType
    waist_type: WaistType
    leg_ratio: LegRatio
    analysis_summary: Optional[str] = None


class ChatRecommendRequest(BaseModel):
    text: str
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    body_context: Optional[ChatBodyContext] = None


class ChatRecommendResponse(BaseModel):
    reply: str
    session_id: str
    parsed_result: StyleParsedResult
    recommend_result: Optional[RecommendResult] = None
