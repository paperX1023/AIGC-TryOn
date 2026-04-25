from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.user import UserResponse
from app.services.user_service import get_user_by_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserResponse:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")

    return get_user_by_token(credentials.credentials)


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserResponse | None:
    if credentials is None:
        return None

    return get_user_by_token(credentials.credentials)


def resolve_request_user_id(
    requested_user_id: int | None,
    current_user: UserResponse | None,
) -> int | None:
    if current_user is None:
        return requested_user_id

    if requested_user_id is not None and requested_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能访问其他用户的数据",
        )

    return current_user.id
