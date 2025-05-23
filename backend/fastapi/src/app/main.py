from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.v1 import router as v1_router
from src.app.base_settings import LogFormat
from src.app.log import configure_logging
from src.app.settings import Settings

from fastapi_observer import setup_observer
from fastapi_observer.config import ObserverConfig

config = Settings()

configure_logging(config.log_format == LogFormat.json)


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_routers(app: FastAPI) -> None:
    app.include_router(v1_router, prefix=config.PATH_PREFIX)

    @app.get("/health")
    def get_health():
        return {"result": "ok"}

    @app.get("/ready")
    def get_ready():
        return {"result": "ok"}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


def create_app(*args, **kwargs) -> FastAPI:
    app = FastAPI(docs_url="/swagger", lifespan=lifespan)
    setup_observer(app, ObserverConfig(
        service_name='Secure_Messanger',
        sensitive_headers=("authorization",),
        sensitive_body_fields=("password",)
    ))
    #configure_logging()
    setup_middleware(app)
    setup_routers(app)

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()

    uvicorn.run(app, host="0.0.0.0", port=config.port)
