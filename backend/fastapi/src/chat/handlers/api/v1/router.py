from typing import Annotated

from starlette import status

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from src.app.log_route import LogRoute
from src.app.utils.exceptions.decorator import handle_domain_error
from src.chat.depends import get_chat_repository
from src.chat.repositories import ChatRepository
from src.chat.schemas.api.v1 import ChatCreate, ChatResponse, ChatUpdate

router = APIRouter(route_class=LogRoute)


@router.post("", response_model=ChatResponse)
@handle_domain_error
async def create_chat(
    payload: ChatCreate,
    repository: Annotated[ChatRepository, Depends(get_chat_repository)],
) -> ORJSONResponse:
    chat = await repository.create(payload)
    return ORJSONResponse(
        content=ChatResponse.model_validate(chat, from_attributes=True).model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("/{chat_id}", response_model=ChatResponse)
@handle_domain_error
async def get_chat(
    chat_id: int,
    repository: Annotated[ChatRepository, Depends(get_chat_repository)],
) -> ORJSONResponse:
    chat = await repository.get_by_id(chat_id)
    return ORJSONResponse(
        content=ChatResponse.model_validate(chat, from_attributes=True).model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("", response_model=list[ChatResponse])
@handle_domain_error
async def get_all_chats(
    repository: Annotated[ChatRepository, Depends(get_chat_repository)],
) -> ORJSONResponse:
    chats = await repository.get_all()
    return ORJSONResponse(
        content=[ChatResponse.model_validate(c, from_attributes=True).model_dump(mode="json") for c in chats],
        status_code=status.HTTP_200_OK,
    )


@router.put("/{chat_id}", response_model=ChatResponse)
@handle_domain_error
async def update_chat(
    chat_id: int,
    payload: ChatUpdate,
    repository: Annotated[ChatRepository, Depends(get_chat_repository)],
) -> ORJSONResponse:
    updated_chat = await repository.update(chat_id, payload)
    return ORJSONResponse(
        content=ChatResponse.model_validate(updated_chat, from_attributes=True).model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_domain_error
async def delete_chat(
    chat_id: int,
    repository: Annotated[ChatRepository, Depends(get_chat_repository)],
) -> None:
    await repository.delete(chat_id)


@router.get("/by-user/{user_id}", response_model=list[ChatResponse])
@handle_domain_error
async def get_chats_by_user(
    user_id: int,
    repository: Annotated[ChatRepository, Depends(get_chat_repository)],
) -> ORJSONResponse:
    """Получение всех чатов, в которых участвует пользователь."""
    chats = await repository.get_chats_by_user(user_id)
    return ORJSONResponse(
        [ChatResponse.model_validate(chat, from_attributes=True).model_dump(mode="json") for chat in chats],
        status_code=status.HTTP_200_OK,
    )
