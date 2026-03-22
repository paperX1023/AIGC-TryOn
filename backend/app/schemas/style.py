from pydantic import BaseModel
from typing import List


class StyleParseRequest(BaseModel):
    text: str


class StyleParsedResult(BaseModel):
    styles: List[str]
    scene: str
    goals: List[str]


class StyleParseResponse(BaseModel):
    raw_text: str
    parsed_result: StyleParsedResult