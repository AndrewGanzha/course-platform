from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI

from app.infrastructure.config import get_settings
from app.presentation.api.dependencies import ApiProvider
from app.presentation.api.handlers import register_exception_handlers
from app.presentation.api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await app.state.dishka_container.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.api.title,
        debug=settings.api.debug,
        lifespan=lifespan,
    )
    register_exception_handlers(app)
    app.include_router(api_router)
    container = make_async_container(ApiProvider(), FastapiProvider())
    setup_dishka(container=container, app=app)
    return app


app = create_app()
