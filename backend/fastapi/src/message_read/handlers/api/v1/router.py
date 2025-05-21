from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from starlette import status

from src.app.log_route import LogRoute
from src.message_read.repositories import MessageReadRepository
from src.message_read.schemas.api.v1 import MessageReadCreate, MessageReadResponse, MessageReadBulkCreate
from src.message_read.depends import get_message_read_repository
from src.app.utils.exceptions.decorator import handle_domain_error

router = APIRouter(route_class=LogRoute)


@router.post("", response_model=MessageReadResponse)
@handle_domain_error
async def create_message_read(
    payload: MessageReadCreate,
    repository: Annotated[MessageReadRepository, Depends(get_message_read_repository)],
) -> ORJSONResponse:
    read = await repository.create(payload)
    return ORJSONResponse(
        content=MessageReadResponse.model_validate(read, from_attributes=True).model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("/check", response_model=bool)
@handle_domain_error
async def has_user_read(
    message_id: int,
    user_id: int,
    repository: Annotated[MessageReadRepository, Depends(get_message_read_repository)],
) -> ORJSONResponse:
    result = await repository.has_user_read(message_id, user_id)
    return ORJSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.get("/by-message/{message_id}", response_model=list[MessageReadResponse])
@handle_domain_error
async def get_readers_by_message(
    message_id: int,
    repository: Annotated[MessageReadRepository, Depends(get_message_read_repository)],
) -> ORJSONResponse:
    result = await repository.get_by_message(message_id)
    return ORJSONResponse(
        content=[MessageReadResponse.model_validate(r, from_attributes=True).model_dump(mode="json") for r in result],
        status_code=status.HTTP_200_OK,
    )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
@handle_domain_error
async def delete_read_for_user(
    message_id: int,
    user_id: int,
    repository: Annotated[MessageReadRepository, Depends(get_message_read_repository)],
) -> None:
    await repository.delete_for_user(message_id, user_id)


@router.post("/bulk", status_code=status.HTTP_204_NO_CONTENT)
@handle_domain_error
async def mark_messages_as_read_bulk(
    payload: MessageReadBulkCreate,
    repository: Annotated[MessageReadRepository, Depends(get_message_read_repository)],
) -> None:
    await repository.mark_many_as_read(
        message_ids=payload.message_ids,
        user_id=payload.user_id,
    )