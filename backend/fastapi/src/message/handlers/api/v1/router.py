from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import ORJSONResponse
from starlette import status

from src.app.log_route import LogRoute
from src.app.utils.auth import get_current_user
from src.app.utils.exceptions.decorator import handle_domain_error
from src.message.schemas.api.v1 import (
    MessageCreate,
    MessageResponse,
)
from src.message.depends import get_message_repository
from src.message.repositories import MessageRepository

from jose import jwt, JWTError

from cent import AsyncClient, PublishRequest, CentApiResponseError

from src.message_read.depends import get_message_read_repository
from src.message_read.repositories import MessageReadRepository
from src.user.models import User

CENTRIFUGO_API_URL = "https://a085-18-153-55-148.ngrok-free.app/api"
API_KEY = "super_api_key"

# Создаем клиент Centrifugo
centrifugo_client = AsyncClient(CENTRIFUGO_API_URL, API_KEY)

router = APIRouter(route_class=LogRoute)


async def publish_message_to_centrifugo(channel: str, data: dict):
    """Функция для публикации сообщений в Centrifugo."""
    try:
        request = PublishRequest(channel=channel, data=data)
        result = await centrifugo_client.publish(request)
        return result
    except CentApiResponseError as e:
        print(f"Ошибка при публикации сообщения в Centrifugo: {e}")
    except Exception as e:
        print(f"Ошибка при публикации сообщения в Centrifugo: {e}")
        raise e

@router.post("", response_model=Optional[MessageResponse])
@handle_domain_error
async def create_message(
        payload: MessageCreate,
        repository: Annotated[MessageRepository, Depends(get_message_repository)],
) -> ORJSONResponse:
    message = await repository.create(payload)

    channel = f"chat_{payload.chat_id}"
    message_data = {
        "message": payload.encrypted_payload.decode("utf-8"),
        "sender": payload.sender_id
    }
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
    print([
        MessageResponse(
            id=msg.id,
            chat_id=msg.chat_id,
            sender_id=msg.sender_id,
            encrypted_payload=msg.encrypted_payload,
            created_at=msg.created_at,
            is_read=msg.id in read_ids
        ).model_dump(mode='json')
        for msg in messages
    ])
    return ORJSONResponse([
        MessageResponse(
            id=msg.id,
            chat_id=msg.chat_id,
            sender_id=msg.sender_id,
            encrypted_payload=msg.encrypted_payload,
            created_at=msg.created_at,
            is_read=msg.id in read_ids
        ).model_dump(mode='json')
        for msg in messages
    ])


@router.get("/centrifugo/token")
def generate_token(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    now = datetime.utcnow()
    exp = now + timedelta(minutes=120)
    centrifugo_token = jwt.encode({"sub": str(user_id), "exp": exp}, 'super_client_key', algorithm="HS256")
    return {"token": centrifugo_token}