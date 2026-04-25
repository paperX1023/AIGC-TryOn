from pydantic import BaseModel
from typing import List

from app.schemas.taxonomy import (
    BodyShape,
    Gender,
    GoalTag,
    LegRatio,
    SceneTag,
    ShoulderType,
    StyleTag,
    WaistType,
)


class RecommendRequest(BaseModel):
    gender: Gender = Gender.UNKNOWN
    body_shape: BodyShape
    shoulder_type: ShoulderType
    waist_type: WaistType
    leg_ratio: LegRatio
    styles: List[StyleTag]
    scene: SceneTag
    goals: List[GoalTag]


class RecommendInputSummary(BaseModel):
    gender: Gender
    body_shape: BodyShape
    shoulder_type: ShoulderType
    waist_type: WaistType
    leg_ratio: LegRatio
    styles: List[StyleTag]
    scene: SceneTag
    goals: List[GoalTag]


class RecommendItem(BaseModel):
    name: str
    category: str
    target_gender: Gender


class RecommendResult(BaseModel):
    recommended_items: List[str]
    categorized_items: List[RecommendItem]
    recommended_style_direction: str
    reason: str


class RecommendResponse(BaseModel):
    input_summary: RecommendInputSummary
    recommend_result: RecommendResult
