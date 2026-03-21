from pydantic import BaseModel
from typing import List


class RecommendRequest(BaseModel):
    gender: str = "未知"
    body_shape: str
    shoulder_type: str
    waist_type: str
    leg_ratio: str
    styles: List[str]
    scene: str
    goals: List[str]


class RecommendInputSummary(BaseModel):
    gender: str
    body_shape: str
    shoulder_type: str
    waist_type: str
    leg_ratio: str
    styles: List[str]
    scene: str
    goals: List[str]


class RecommendItem(BaseModel):
    name: str
    category: str
    target_gender: str


class RecommendResult(BaseModel):
    recommended_items: List[str]
    categorized_items: List[RecommendItem]
    recommended_style_direction: str
    reason: str


class RecommendResponse(BaseModel):
    input_summary: RecommendInputSummary
    recommend_result: RecommendResult
