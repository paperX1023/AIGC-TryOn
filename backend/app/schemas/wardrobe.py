from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class WardrobeDetectionResponse(BaseModel):
    passed: bool
    score: float = Field(ge=0, le=1)
    message: str
    checks: dict[str, bool]


class WardrobeItemResponse(BaseModel):
    id: str
    numeric_id: int | None = None
    user_id: int | None = None
    name: str
    category: str
    image_path: str
    image_url: str
    source: str
    detection_result: WardrobeDetectionResponse | None = None
    created_at: datetime | None = None


class WardrobeListResponse(BaseModel):
    items: list[WardrobeItemResponse] = Field(default_factory=list)
