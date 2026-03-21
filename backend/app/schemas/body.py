from pydantic import BaseModel


class BodyAnalyzeResponse(BaseModel):
    gender: str
    body_shape: str
    shoulder_type: str
    waist_type: str
    leg_ratio: str
    analysis_summary: str
    image_path: str
    image_url: str
