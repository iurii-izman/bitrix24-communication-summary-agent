from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.admin import router as admin_router
from app.api.communications import router as communications_router
from app.api.health import router as health_router
from app.database import create_engine_from_settings, create_session_factory, init_db
from app.security import InMemoryRateLimiter
from app.services.worker import WorkerService
from app.settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = create_engine_from_settings(resolved_settings)
        init_db(engine)
        app.state.settings = resolved_settings
        app.state.engine = engine
        app.state.session_factory = create_session_factory(engine)
        app.state.rate_limiter = InMemoryRateLimiter(
            max_requests=resolved_settings.rate_limit_max_requests,
            window_seconds=resolved_settings.rate_limit_window_seconds,
        )
        app.state.worker_service = WorkerService(resolved_settings)
        yield
        engine.dispose()

    app = FastAPI(
        title=resolved_settings.app_name,
        debug=resolved_settings.app_debug,
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(communications_router)
    app.include_router(admin_router)
    return app


app = create_app()
