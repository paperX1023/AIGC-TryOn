from pydantic import BaseModel
from typing import List

from app.schemas.taxonomy import GoalTag, SceneTag, StyleTag


class StyleParseRequest(BaseModel):
    text: str


class StyleParsedResult(BaseModel):
    styles: List[StyleTag]
    scene: SceneTag
    goals: List[GoalTag]


class StyleParseResponse(BaseModel):
    raw_text: str
    parsed_result: StyleParsedResult
