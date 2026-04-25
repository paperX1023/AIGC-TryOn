from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.schemas.user import (
    AuthResponse,
    UserCreateRequest,
    UserDashboardResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services.user_service import (
    create_user,
    get_user,
    get_user_by_token,
    get_user_dashboard,
    list_users,
    login_user,
    register_user,
    update_user,
)

router = APIRouter()


@router.post("/auth/register", response_model=AuthResponse)
def register_endpoint(data: UserRegisterRequest):
    return register_user(data)


@router.post("/auth/login", response_model=AuthResponse)
def login_endpoint(data: UserLoginRequest):
    return login_user(data)


@router.get("/auth/me", response_model=UserResponse)
def get_current_user_endpoint(user: UserResponse = Depends(get_current_user)):
    return user


@router.get("/users/me", response_model=UserResponse)
def get_me_endpoint(user: UserResponse = Depends(get_current_user)):
    return user


@router.post("/users", response_model=UserResponse)
def create_user_endpoint(data: UserCreateRequest):
    return create_user(data)


@router.get("/users", response_model=list[UserResponse])
def list_users_endpoint(user: UserResponse = Depends(get_current_user)):
    return [user]


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: int, user: UserResponse = Depends(get_current_user)):
    if user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不能查看其他用户")

    return get_user(user_id)


@router.get("/users/me/dashboard", response_model=UserDashboardResponse)
def get_my_dashboard_endpoint(user: UserResponse = Depends(get_current_user)):
    return get_user_dashboard(user.id)


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user_endpoint(
    user_id: int,
    data: UserUpdateRequest,
    user: UserResponse = Depends(get_current_user),
):
    if user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不能修改其他用户")

    return update_user(user_id, data)


@router.get("/users/{user_id}/dashboard", response_model=UserDashboardResponse)
def get_user_dashboard_endpoint(
    user_id: int,
    user: UserResponse = Depends(get_current_user),
):
    if user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不能查看其他用户数据")

    return get_user_dashboard(user_id)
