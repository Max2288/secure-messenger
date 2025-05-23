from typing import Callable, Any
from functools import wraps
from fastapi import HTTPException, status
import structlog

from src.app.utils.exceptions.schema import DomainError, ItemNotFound

logger = structlog.get_logger(__name__)

def handle_domain_error(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except ItemNotFound as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(error),
            )
        except DomainError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            )
        except HTTPException as http_error:
            raise http_error
        except Exception as error:
            logger.error("Unhandled exception in handler", error = error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error"
            )

    return wrapper
