from datetime import datetime, timedelta
from typing import Annotated, Optional

from jose import jwt
from starlette import status

from fastapi import APIRouter, Depends, Header
from fastapi.responses import ORJSONResponse
from src.app.log_route import LogRoute
from src.app.settings import Settings
from src.app.utils.auth import get_current_user
from src.app.utils.centrifugo import publish_message_to_centrifugo
from src.app.utils.exceptions.decorator import handle_domain_error
from src.app.utils.jwt import get_user_id_from_token
from src.message.depends import get_message_repository
from src.message.repositories import MessageRepository
from src.message.schemas.api.v1 import MessageCreate, MessageResponse
from src.message_read.depends import get_message_read_repository
from src.message_read.repositories import MessageReadRepository
from src.user.models import User

settings = Settings()


router = APIRouter(route_class=LogRoute)


@router.post("", response_model=Optional[MessageResponse])
@handle_domain_error
async def create_message(
    payload: MessageCreate,
    repository: Annotated[MessageRepository, Depends(get_message_repository)],
) -> ORJSONResponse:
    message = await repository.create(payload)

    channel = f"chat_{payload.chat_id}"
    message_data = {"message": payload.encrypted_payload.decode("utf-8"), "sender": payload.sender_id}
    await publish_message_to_centrifugo(channel, message_data)

    return ORJSONResponse(
        content=MessageResponse.model_validate(message, from_attributes=True).model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("/{message_id}", response_model=MessageResponse)
@handle_domain_error
async def get_message(
    message_id: int,
    repository: Annotated[MessageRepository, Depends(get_message_repository)],
) -> ORJSONResponse:
    message = await repository.get_by_id(message_id)
    return ORJSONResponse(
        content=MessageResponse.model_validate(message, from_attributes=True).model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
    )


@router.get("", response_model=list[MessageResponse])
@handle_domain_error
async def get_all_messages(
    repository: Annotated[MessageRepository, Depends(get_message_repository)],
) -> ORJSONResponse:
    messages = await repository.get_all()
    return ORJSONResponse(
        content=[MessageResponse.model_validate(msg, from_attributes=True).model_dump(mode="json") for msg in messages],
        status_code=status.HTTP_200_OK,
    )


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_domain_error
async def delete_message(
    message_id: int,
    repository: Annotated[MessageRepository, Depends(get_message_repository)],
) -> None:
    await repository.delete(message_id)


@router.get("/by-chat/{chat_id}", response_model=list[MessageResponse])
@handle_domain_error
async def get_messages_by_chat_id(
    chat_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[MessageRepository, Depends(get_message_repository)],
    read_repo: Annotated[MessageReadRepository, Depends(get_message_read_repository)],
) -> ORJSONResponse:
    """Получение всех сообщений по ID чата."""
    messages = await repository.get_by_chat_id(chat_id)
    participant_ids = [m.sender_id for m in messages if m.sender_id != current_user.id]
    read_ids = await read_repo.get_read_message_ids(participant_ids, [m.id for m in messages])
    return ORJSONResponse(
        [
            MessageResponse(
                id=msg.id,
                chat_id=msg.chat_id,
                sender_id=msg.sender_id,
                encrypted_payload=msg.encrypted_payload,
                created_at=msg.created_at,
                is_read=msg.id in read_ids,
            ).model_dump(mode="json")
            for msg in messages
        ]
    )


@router.get("/centrifugo/token")
def generate_centrifugo_token(authorization: str = Header(...)):
    user_id = get_user_id_from_token(authorization)
    now = datetime.utcnow()
    exp = now + timedelta(minutes=120)
    centrifugo_token = jwt.encode(
        {"sub": str(user_id), "exp": exp}, settings.CENTRIFUGO_CLIENT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return {"token": centrifugo_token}
