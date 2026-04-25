from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

from fastapi import HTTPException, status
from sqlalchemy import desc, or_, select

from app.db.models import BodyAnalysisRecord, ChatSession, RecommendationRecord, TryOnRecord, User
from app.db.session import is_database_enabled, optional_session_scope
from app.core.config import settings
from app.schemas.user import (
    AuthResponse,
    BodyAnalysisRecordResponse,
    ChatSessionSummaryResponse,
    RecommendationRecordResponse,
    TryOnRecordResponse,
    UserCreateRequest,
    UserDashboardResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services.persistence_service import count_chat_messages_by_session

_PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
_PASSWORD_HASH_ITERATIONS = 260_000


def _ensure_database_enabled():
    if not is_database_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="当前未配置数据库，请先设置 DATABASE_URL 或 DB_HOST/DB_USER/DB_PASSWORD",
        )


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None


def _hash_password(password: str) -> str:
    salt = secrets.token_urlsafe(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        _PASSWORD_HASH_ITERATIONS,
    )
    return f"{_PASSWORD_HASH_ALGORITHM}${_PASSWORD_HASH_ITERATIONS}${salt}${digest.hex()}"


def _verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False

    try:
        algorithm, iterations, salt, stored_digest = password_hash.split("$", 3)
        if algorithm != _PASSWORD_HASH_ALGORITHM:
            return False

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()
    except (TypeError, ValueError):
        return False

    return hmac.compare_digest(digest, stored_digest)


def _encode_base64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _decode_base64url(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))


def _sign_token_payload(payload: str) -> str:
    signature = hmac.new(
        settings.auth_secret_key.encode("utf-8"),
        payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return _encode_base64url(signature)


def _create_access_token(user_id: int) -> str:
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + settings.auth_token_expire_minutes * 60,
    }
    payload_text = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    encoded_payload = _encode_base64url(payload_text.encode("utf-8"))
    return f"{encoded_payload}.{_sign_token_payload(encoded_payload)}"


def _decode_access_token(token: str) -> int:
    try:
        encoded_payload, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态无效") from exc

    expected_signature = _sign_token_payload(encoded_payload)
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态无效")

    try:
        payload = json.loads(_decode_base64url(encoded_payload).decode("utf-8"))
        user_id = int(payload["sub"])
        expires_at = int(payload["exp"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态无效") from exc

    if expires_at < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态已过期")

    return user_id


def _serialize_user(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar_url=user.avatar_url,
        gender=user.gender,
        birthday=user.birthday,
        height_cm=float(user.height_cm) if user.height_cm is not None else None,
        weight_kg=float(user.weight_kg) if user.weight_kg is not None else None,
        preferred_styles=user.preferred_styles or [],
        bio=user.bio,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _find_user_by_account(db, account: str) -> User | None:
    normalized_account = account.strip()
    if not normalized_account:
        return None

    return db.scalar(
        select(User)
        .where(
            or_(
                User.username == normalized_account,
                User.email == normalized_account,
                User.phone == normalized_account,
            )
        )
        .limit(1)
    )


def _build_user(data: UserCreateRequest | UserRegisterRequest, password: str | None = None) -> User:
    return User(
        username=data.username.strip(),
        password_hash=_hash_password(password) if password else None,
        nickname=_normalize_optional_text(data.nickname),
        email=_normalize_optional_text(data.email),
        phone=_normalize_optional_text(data.phone),
        avatar_url=_normalize_optional_text(data.avatar_url),
        gender=data.gender.value if data.gender else None,
        birthday=data.birthday,
        height_cm=data.height_cm,
        weight_kg=data.weight_kg,
        preferred_styles=[item.value for item in data.preferred_styles] or None,
        bio=_normalize_optional_text(data.bio),
    )


def _ensure_unique_user_fields(db, data: UserCreateRequest | UserRegisterRequest) -> None:
    username = data.username.strip()
    email = _normalize_optional_text(data.email)
    phone = _normalize_optional_text(data.phone)

    if db.scalar(select(User).where(User.username == username).limit(1)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")

    if email and db.scalar(select(User).where(User.email == email).limit(1)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已存在")

    if phone and db.scalar(select(User).where(User.phone == phone).limit(1)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="手机号已存在")


def _auth_response(user: User) -> AuthResponse:
    return AuthResponse(
        user=_serialize_user(user),
        access_token=_create_access_token(user.id),
    )


def _serialize_body_record(record: BodyAnalysisRecord) -> BodyAnalysisRecordResponse:
    return BodyAnalysisRecordResponse(
        id=record.id,
        user_id=record.user_id,
        image_path=record.image_path,
        image_url=record.image_url,
        gender=record.gender,
        body_shape=record.body_shape,
        shoulder_type=record.shoulder_type,
        waist_type=record.waist_type,
        leg_ratio=record.leg_ratio,
        analysis_summary=record.analysis_summary,
        created_at=record.created_at,
    )


def _serialize_chat_session(db, session: ChatSession) -> ChatSessionSummaryResponse:
    return ChatSessionSummaryResponse(
        id=session.id,
        session_id=session.session_code,
        user_id=session.user_id,
        title=session.title,
        status=session.status,
        latest_body_analysis_id=session.latest_body_analysis_id,
        message_count=count_chat_messages_by_session(db, session.id),
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _serialize_recommendation(record: RecommendationRecord) -> RecommendationRecordResponse:
    return RecommendationRecordResponse(
        id=record.id,
        user_id=record.user_id,
        chat_session_id=record.chat_session_id,
        source=record.source,
        input_summary=record.input_summary,
        recommend_result=record.recommend_result,
        created_at=record.created_at,
    )


def _serialize_tryon(record: TryOnRecord) -> TryOnRecordResponse:
    return TryOnRecordResponse(
        id=record.id,
        user_id=record.user_id,
        chat_session_id=record.chat_session_id,
        body_analysis_record_id=record.body_analysis_record_id,
        person_image_path=record.person_image_path,
        person_image_url=record.person_image_url,
        cloth_image_path=record.cloth_image_path,
        cloth_image_url=record.cloth_image_url,
        result_image_path=record.result_image_path,
        result_image_url=record.result_image_url,
        status=record.status,
        message=record.message,
        source=record.source,
        created_at=record.created_at,
    )


def create_user(data: UserCreateRequest) -> UserResponse:
    _ensure_database_enabled()

    with optional_session_scope() as db:
        if db is None:
            raise RuntimeError("数据库会话初始化失败")

        _ensure_unique_user_fields(db, data)

        user = _build_user(data, password=data.password)
        db.add(user)
        db.flush()
        db.refresh(user)
        return _serialize_user(user)


def register_user(data: UserRegisterRequest) -> AuthResponse:
    _ensure_database_enabled()

    with optional_session_scope() as db:
        if db is None:
            raise RuntimeError("数据库会话初始化失败")

        _ensure_unique_user_fields(db, data)

        user = _build_user(data, password=data.password)
        db.add(user)
        db.flush()
        db.refresh(user)
        return _auth_response(user)


def login_user(data: UserLoginRequest) -> AuthResponse:
    _ensure_database_enabled()

    with optional_session_scope() as db:
        if db is None:
            raise RuntimeError("数据库会话初始化失败")

        user = _find_user_by_account(db, data.account)
        if user is None or not _verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")

        return _auth_response(user)


def get_user_by_token(token: str) -> UserResponse:
    user_id = _decode_access_token(token)
    return get_user(user_id)


def list_users() -> list[UserResponse]:
    _ensure_database_enabled()

    with optional_session_scope() as db:
        if db is None:
            return []
        users = db.scalars(select(User).order_by(User.id.desc())).all()
        return [_serialize_user(user) for user in users]


def get_user(user_id: int) -> UserResponse:
    _ensure_database_enabled()

    with optional_session_scope() as db:
        if db is None:
            raise RuntimeError("数据库会话初始化失败")
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
        return _serialize_user(user)


def update_user(user_id: int, data: UserUpdateRequest) -> UserResponse:
    _ensure_database_enabled()

    with optional_session_scope() as db:
        if db is None:
            raise RuntimeError("数据库会话初始化失败")

        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        payload = data.model_dump(exclude_unset=True)
        if "email" in payload:
            payload["email"] = _normalize_optional_text(payload["email"])
        if "phone" in payload:
            payload["phone"] = _normalize_optional_text(payload["phone"])
        if "nickname" in payload:
            payload["nickname"] = _normalize_optional_text(payload["nickname"])
        if "avatar_url" in payload:
            payload["avatar_url"] = _normalize_optional_text(payload["avatar_url"])
        if "bio" in payload:
            payload["bio"] = _normalize_optional_text(payload["bio"])

        if "email" in payload and payload["email"] and payload["email"] != user.email:
            if db.scalar(select(User).where(User.email == payload["email"]).limit(1)):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已存在")

        if "phone" in payload and payload["phone"] and payload["phone"] != user.phone:
            if db.scalar(select(User).where(User.phone == payload["phone"]).limit(1)):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="手机号已存在")

        for key, value in payload.items():
            if key == "gender":
                setattr(user, key, value.value if value else None)
            elif key == "preferred_styles":
                setattr(user, key, [item.value for item in value] if value else [])
            else:
                setattr(user, key, value)

        db.flush()
        db.refresh(user)
        return _serialize_user(user)


def get_user_dashboard(user_id: int) -> UserDashboardResponse:
    _ensure_database_enabled()

    with optional_session_scope() as db:
        if db is None:
            raise RuntimeError("数据库会话初始化失败")

        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        latest_body_analysis = db.scalar(
            select(BodyAnalysisRecord)
            .where(BodyAnalysisRecord.user_id == user_id)
            .order_by(desc(BodyAnalysisRecord.created_at))
            .limit(1)
        )
        recent_sessions = db.scalars(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.updated_at))
            .limit(10)
        ).all()
        recent_recommendations = db.scalars(
            select(RecommendationRecord)
            .where(RecommendationRecord.user_id == user_id)
            .order_by(desc(RecommendationRecord.created_at))
            .limit(10)
        ).all()
        recent_tryons = db.scalars(
            select(TryOnRecord)
            .where(TryOnRecord.user_id == user_id)
            .order_by(desc(TryOnRecord.created_at))
            .limit(10)
        ).all()

        return UserDashboardResponse(
            user=_serialize_user(user),
            latest_body_analysis=_serialize_body_record(latest_body_analysis) if latest_body_analysis else None,
            recent_chat_sessions=[_serialize_chat_session(db, session) for session in recent_sessions],
            recent_recommendations=[_serialize_recommendation(record) for record in recent_recommendations],
            recent_tryons=[_serialize_tryon(record) for record in recent_tryons],
        )
