from fastapi import APIRouter, Request
from sqlalchemy import text

from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    db_ok = True
    try:
        with request.app.state.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        db_ok = False
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        app_mode=settings.app_mode,
        ai_provider=settings.ai_provider,
        bitrix_mode=settings.bitrix_mode,
        allow_bitrix_write=settings.allow_bitrix_write,
        db_ok=db_ok,
    )
