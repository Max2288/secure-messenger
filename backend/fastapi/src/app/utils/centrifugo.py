import structlog
from cent import AsyncClient, CentApiResponseError, PublishRequest

from src.app.settings import Settings

settings = Settings()

centrifugo_client = AsyncClient(settings.CENTRIFUGO_API_URL, settings.CENTRIFUGO_API_KEY)

logger = structlog.get_logger(__name__)


async def publish_message_to_centrifugo(channel: str, data: dict):
    """Функция для публикации сообщений в Centrifugo."""
    try:
        request = PublishRequest(channel=channel, data=data)
        result = await centrifugo_client.publish(request)
        return result
    except CentApiResponseError as e:
        logger.error(f"Ошибка при публикации сообщения в Centrifugo: {e}")
