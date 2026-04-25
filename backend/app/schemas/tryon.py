from pydantic import BaseModel


class TryOnResponse(BaseModel):
    record_id: int | None = None
    person_image_path: str
    person_image_url: str
    cloth_image_path: str
    cloth_image_url: str
    result_image_path: str
    result_image_url: str
    status: str
    message: str
