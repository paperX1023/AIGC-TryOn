from pydantic import BaseModel

from app.schemas.taxonomy import BodyShape, Gender, LegRatio, ShoulderType, WaistType


class BodyAnalyzeResponse(BaseModel):
    record_id: int | None = None
    gender: Gender
    body_shape: BodyShape
    shoulder_type: ShoulderType
    waist_type: WaistType
    leg_ratio: LegRatio
    analysis_summary: str
    image_path: str
    image_url: str
