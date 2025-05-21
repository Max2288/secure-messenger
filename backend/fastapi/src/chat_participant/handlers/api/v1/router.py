from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from starlette import status

from src.app.log_route import LogRoute
from src.app.utils.exceptions.decorator import handle_domain_error
from src.chat_participant.schemas.api.v1 import (
    ChatParticipantCreate,
    ChatParticipantResponse,
)
from src.chat_participant.depends import get_chat_participant_repository
from src.chat_participant.repositories import ChatParticipantRepository

router = APIRouter(route_class=LogRoute)


@router.post("", response_model=Optional[ChatParticipantResponse])
@handle_domain_error
async def create_chat_participant(
    payload: ChatParticipantCreate,
    repository: Annotated[ChatParticipantRepository, Depends(get_chat_participant_repository)],
) -> ORJSONResponse:
    participant = await repository.create(payload)
    return ORJSONResponse(
        content=ChatParticipantResponse.model_validate(participant, from_attributes=True).model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("/{participant_id}", response_model=ChatParticipantResponse)
@handle_domain_error
async def get_chat_participant(
    participant_id: int,
    repository: Annotated[ChatParticipantRepository, Depends(get_chat_participant_repository)],
) -> ORJSONResponse:
    participant = await repository.get_by_id(participant_id)
    return ORJSONResponse(
        content=ChatParticipantResponse.model_validate(participant, from_attributes=True).model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("", response_model=list[ChatParticipantResponse])
@handle_domain_error
async def get_all_chat_participants(
    repository: Annotated[ChatParticipantRepository, Depends(get_chat_participant_repository)],
) -> ORJSONResponse:
    participants = await repository.get_all()
    return ORJSONResponse(
        content=[ChatParticipantResponse.model_validate(p, from_attributes=True).model_dump(mode="json") for p in participants],
        status_code=status.HTTP_200_OK,
    )


@router.delete("/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_domain_error
async def delete_chat_participant(
    participant_id: int,
    repository: Annotated[ChatParticipantRepository, Depends(get_chat_participant_repository)],
) -> None:
    await repository.delete(participant_id)


@router.get("/by-chat/{chat_id}", response_model=list[ChatParticipantResponse])
@handle_domain_error
async def get_users_by_chat(
    chat_id: int,
    repository: Annotated[ChatParticipantRepository, Depends(get_chat_participant_repository)],
) -> ORJSONResponse:
    """Получение всех пользователей в чате."""
    users = await repository.get_users_by_chat(chat_id)
    return ORJSONResponse(
        [ChatParticipantResponse.model_validate(p, from_attributes=True).model_dump(mode="json") for p in users],
        status_code=status.HTTP_200_OK,
    )
