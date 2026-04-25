from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.taxonomy import Gender, StyleTag


class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    nickname: str | None = Field(default=None, max_length=64)
    email: str | None = Field(default=None, max_length=128)
    phone: str | None = Field(default=None, max_length=32)
    avatar_url: str | None = None
    gender: Gender | None = None
    birthday: date | None = None
    height_cm: float | None = Field(default=None, ge=0)
    weight_kg: float | None = Field(default=None, ge=0)
    preferred_styles: list[StyleTag] = Field(default_factory=list)
    bio: str | None = None


class UserCreateRequest(UserBase):
    password: str | None = Field(default=None, min_length=6, max_length=128)


class UserRegisterRequest(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserLoginRequest(BaseModel):
    account: str = Field(min_length=2, max_length=128)
    password: str = Field(min_length=1, max_length=128)


class UserUpdateRequest(BaseModel):
    nickname: str | None = Field(default=None, max_length=64)
    email: str | None = Field(default=None, max_length=128)
    phone: str | None = Field(default=None, max_length=32)
    avatar_url: str | None = None
    gender: Gender | None = None
    birthday: date | None = None
    height_cm: float | None = Field(default=None, ge=0)
    weight_kg: float | None = Field(default=None, ge=0)
    preferred_styles: list[StyleTag] | None = None
    bio: str | None = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class BodyAnalysisRecordResponse(BaseModel):
    id: int
    user_id: int
    image_path: str
    image_url: str
    gender: str
    body_shape: str
    shoulder_type: str
    waist_type: str
    leg_ratio: str
    analysis_summary: str
    created_at: datetime


class ChatSessionSummaryResponse(BaseModel):
    id: int
    session_id: str
    user_id: int | None = None
    title: str | None = None
    status: str
    latest_body_analysis_id: int | None = None
    message_count: int = 0
    created_at: datetime
    updated_at: datetime


class RecommendationRecordResponse(BaseModel):
    id: int
    user_id: int
    chat_session_id: int | None = None
    source: str
    input_summary: dict
    recommend_result: dict
    created_at: datetime


class TryOnRecordResponse(BaseModel):
    id: int
    user_id: int | None = None
    chat_session_id: int | None = None
    body_analysis_record_id: int | None = None
    person_image_path: str
    person_image_url: str
    cloth_image_path: str
    cloth_image_url: str
    result_image_path: str
    result_image_url: str
    status: str
    message: str
    source: str
    created_at: datetime


class UserDashboardResponse(BaseModel):
    user: UserResponse
    latest_body_analysis: BodyAnalysisRecordResponse | None = None
    recent_chat_sessions: list[ChatSessionSummaryResponse] = Field(default_factory=list)
    recent_recommendations: list[RecommendationRecordResponse] = Field(default_factory=list)
    recent_tryons: list[TryOnRecordResponse] = Field(default_factory=list)
