from __future__ import annotations

from enum import Enum
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc, func, select

from app.db.models import (
    BodyAnalysisRecord,
    ChatMessage,
    ChatSession,
    RecommendationRecord,
    TryOnRecord,
    User,
)
from app.db.session import is_database_enabled, optional_session_scope


def _to_json_safe(value: Any):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _to_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_json_safe(item) for item in value]
    return value


def _require_user(db, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到用户 user_id={user_id}",
        )
    return user


def _get_latest_body_analysis_id(db, user_id: int | None) -> int | None:
    if user_id is None:
        return None

    stmt = (
        select(BodyAnalysisRecord.id)
        .where(BodyAnalysisRecord.user_id == user_id)
        .order_by(desc(BodyAnalysisRecord.created_at))
        .limit(1)
    )
    return db.scalar(stmt)


def _get_or_create_chat_session(db, session_code: str, user_id: int | None) -> ChatSession:
    chat_session = db.scalar(
        select(ChatSession).where(ChatSession.session_code == session_code).limit(1)
    )
    if chat_session is None:
        chat_session = ChatSession(
            session_code=session_code,
            user_id=user_id,
            latest_body_analysis_id=_get_latest_body_analysis_id(db, user_id),
            status="active",
        )
        db.add(chat_session)
        db.flush()
        return chat_session

    if user_id is not None and chat_session.user_id is None:
        chat_session.user_id = user_id

    if user_id is not None:
        chat_session.latest_body_analysis_id = _get_latest_body_analysis_id(db, user_id)

    return chat_session


def save_body_analysis_record(user_id: int | None, analyzed_result: dict) -> int | None:
    if user_id is None or not is_database_enabled():
        return None

    with optional_session_scope() as db:
        if db is None:
            return None

        _require_user(db, user_id)
        record = BodyAnalysisRecord(
            user_id=user_id,
            image_path=analyzed_result["image_path"],
            image_url=analyzed_result["image_url"],
            gender=analyzed_result["gender"],
            body_shape=analyzed_result["body_shape"],
            shoulder_type=analyzed_result["shoulder_type"],
            waist_type=analyzed_result["waist_type"],
            leg_ratio=analyzed_result["leg_ratio"],
            analysis_summary=analyzed_result["analysis_summary"],
        )
        db.add(record)
        db.flush()
        return record.id


def save_recommendation_record(
    user_id: int | None,
    session_code: str | None,
    source: str,
    input_summary: dict,
    recommend_result: dict,
) -> int | None:
    if user_id is None or not is_database_enabled():
        return None

    with optional_session_scope() as db:
        if db is None:
            return None

        _require_user(db, user_id)
        chat_session = _get_or_create_chat_session(db, session_code, user_id) if session_code else None

        record = RecommendationRecord(
            user_id=user_id,
            chat_session_id=chat_session.id if chat_session else None,
            source=source,
            input_summary=_to_json_safe(input_summary),
            recommend_result=_to_json_safe(recommend_result),
        )
        db.add(record)
        db.flush()
        return record.id


def save_chat_exchange(
    *,
    user_id: int | None,
    session_code: str,
    user_text: str,
    assistant_reply: str,
    parsed_result: dict,
    recommend_result: dict | None,
) -> None:
    if not is_database_enabled():
        return

    with optional_session_scope() as db:
        if db is None:
            return

        if user_id is not None:
            _require_user(db, user_id)

        chat_session = _get_or_create_chat_session(db, session_code, user_id)
        if not chat_session.title:
            chat_session.title = user_text[:30]

        db.add(
            ChatMessage(
                chat_session_id=chat_session.id,
                role="user",
                content=user_text,
                parsed_result=None,
                recommend_result=None,
            )
        )
        db.add(
            ChatMessage(
                chat_session_id=chat_session.id,
                role="assistant",
                content=assistant_reply,
                parsed_result=_to_json_safe(parsed_result),
                recommend_result=_to_json_safe(recommend_result) if recommend_result else None,
            )
        )

        if user_id is not None and recommend_result:
            db.add(
                RecommendationRecord(
                    user_id=user_id,
                    chat_session_id=chat_session.id,
                    source="chat",
                    input_summary=_to_json_safe(parsed_result),
                    recommend_result=_to_json_safe(recommend_result),
                )
            )


def save_tryon_record(
    *,
    user_id: int | None,
    session_code: str | None,
    tryon_result: dict,
    source: str,
) -> int | None:
    if not is_database_enabled() or (user_id is None and not session_code):
        return None

    with optional_session_scope() as db:
        if db is None:
            return None

        if user_id is not None:
            _require_user(db, user_id)

        chat_session = _get_or_create_chat_session(db, session_code, user_id) if session_code else None
        record = TryOnRecord(
            user_id=user_id,
            chat_session_id=chat_session.id if chat_session else None,
            body_analysis_record_id=_get_latest_body_analysis_id(db, user_id),
            person_image_path=tryon_result["person_image_path"],
            person_image_url=tryon_result["person_image_url"],
            cloth_image_path=tryon_result["cloth_image_path"],
            cloth_image_url=tryon_result["cloth_image_url"],
            result_image_path=tryon_result["result_image_path"],
            result_image_url=tryon_result["result_image_url"],
            status=tryon_result["status"],
            message=tryon_result["message"],
            source=source,
        )
        db.add(record)
        db.flush()
        return record.id


def count_chat_messages_by_session(db, chat_session_id: int) -> int:
    stmt = select(func.count(ChatMessage.id)).where(ChatMessage.chat_session_id == chat_session_id)
    return int(db.scalar(stmt) or 0)
