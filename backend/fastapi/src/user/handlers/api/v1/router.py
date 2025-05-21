from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import ORJSONResponse
from starlette import status

from src.app.log_route import LogRoute
from src.app.utils.auth import get_current_user
from src.app.utils.exceptions.decorator import handle_domain_error
from src.app.utils.jwt import create_access_token
from src.user.models import User
from src.user.repositories import UserRepository
from src.user.schemas.api.v1 import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse, UserLoginRequest,
)
from src.user.depends import get_user_repository

router = APIRouter(route_class=LogRoute)


@router.post("", response_model=UserResponse)
@handle_domain_error
async def create_user(
    payload: UserCreateRequest,
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> ORJSONResponse:
    """Создает нового пользователя."""
    user = await repository.create_user(
        username=payload.username,
        password_hash=payload.password_hash,
        public_key=payload.public_key,
    )
    return ORJSONResponse(
        content=UserResponse.model_validate(user, from_attributes=True).model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/{user_id}", response_model=UserResponse)
@handle_domain_error
async def get_user_by_id(
    user_id: int,
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> ORJSONResponse:
    """Возвращает пользователя по ID."""
    user = await repository.get_by_id(user_id)
    return ORJSONResponse(
        content=UserResponse.model_validate(user, from_attributes=True).model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("", response_model=list[UserResponse])
@handle_domain_error
async def list_users(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> ORJSONResponse:
    """Возвращает список пользователей с пагинацией."""
    users = await repository.list_users(limit=limit, offset=offset)
    return ORJSONResponse(
        [UserResponse.model_validate(u, from_attributes=True).model_dump(mode="json") for u in users],
        status_code=status.HTTP_200_OK,
    )


@router.patch("/{user_id}", response_model=UserResponse)
@handle_domain_error
async def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> ORJSONResponse:
    """Обновляет пользователя по ID."""
    user = await repository.update_user(
        user_id=user_id,
        username=payload.username,
        password_hash=payload.password_hash,
        public_key=payload.public_key,
    )
    return ORJSONResponse(
        content=UserResponse.model_validate(user, from_attributes=True).model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_domain_error
async def delete_user(
    user_id: int,
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> None:
    """Удаляет пользователя по ID."""
    await repository.delete_user(user_id)


@router.post("/login", response_model=UserResponse)
@handle_domain_error
async def login_user(
    payload: UserLoginRequest,
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> ORJSONResponse:
    """Аутентифицирует пользователя по username и password_hash."""
    user = await repository.login_user(
        username=payload.username,
        password_hash=payload.password_hash,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token({"sub": str(user.id)})
    return ORJSONResponse(
        content={
            "access_token": token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user, from_attributes=True).model_dump(mode="json"),
        },
        status_code=status.HTTP_200_OK,
    )




@router.get("/login/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user, from_attributes=True)
