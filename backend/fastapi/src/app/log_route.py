import time
from collections.abc import Callable

import structlog
from orjson import orjson

from fastapi import Request, Response, exceptions
from fastapi.routing import APIRoute

logger = structlog.get_logger(__name__)


class LogRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        """Возвращает пользовательский обработчик маршрута с логированием.

        Raises
        ------
            exceptions.HTTPException: Ошибка HTTP при выполнении запроса.
            exceptions.RequestValidationError: Ошибка валидации запроса.

        Returns
        -------
            Callable: Пользовательский обработчик маршрута.

        """
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Обработчик маршрута с логированием.

            Args:
            ----
                request (Request): Объект запроса.

            Returns:
            -------
                Response: Объект ответа.

            """
            start_time = time.time()
            logger.info("REQ method and URL", method=request.method, url=request.url)

            if request.path_params:
                logger.info("REQ PARAMS:", params=request.path_params)

            logger.info("HEADERS:", headers=request.headers)

            try:
                body = await request.body()
                body_json = orjson.loads(body) if body else {}
                logger.info("REQ BODY:", body=body_json)
            except orjson.JSONDecodeError:
                logger.warning("Request body is not valid JSON")
            except Exception as e:
                logger.exception(f"Error reading request body: {e}")

            try:
                response: Response = await original_route_handler(request)
            except exceptions.HTTPException as e:
                logger.exception("HTTPException: %d, %s" % (e.status_code, e.detail))
                raise
            except exceptions.RequestValidationError as e:
                logger.exception(f"RequestValidationError: {e}")
                raise
            except Exception as e:
                logger.exception(f"Unhandled exception: {e}")
                raise
            else:
                process_time = time.time() - start_time
                logger.info("Route response status_code=%d, processing_time=%.4fs" % (response.status_code, process_time))

            try:
                response_body = response.body
                response_json = orjson.loads(response_body) if response_body else {}
                logger.info("RESP BODY:", body=response_json)
            except orjson.JSONDecodeError:
                logger.warning("Response body is not valid JSON")
            except AttributeError:
                logger.warning("Response body attribute is not available")
            except Exception as e:
                logger.exception(f"Error reading response body: {e}")

            return response

        return custom_route_handler
