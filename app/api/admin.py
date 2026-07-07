from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.models import CommunicationRequestRecord
from app.schemas import CommunicationStatus
from app.security import require_admin_auth
from app.services.communication_service import CommunicationService

router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin_auth)])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
templates.env.filters["pretty_json"] = (
    lambda value: json.dumps(value, ensure_ascii=False, indent=2, default=str)
)
templates.env.filters["status_badge_class"] = lambda value: _badge_class("status", value)
templates.env.filters["priority_badge_class"] = lambda value: _badge_class("priority", value)
templates.env.filters["risk_badge_class"] = lambda value: _badge_class("risk", value)
templates.env.filters["channel_label"] = lambda value: str(value).replace("_", " ").title()


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Annotated[Session, Depends(get_db_session)]) -> HTMLResponse:
    service = CommunicationService()
    stats = service.summary_stats(db)
    context = _base_context(request, active_page="dashboard", stats=stats)
    context.update(
        {
            "stats": stats,
            "records": service.list_records(db, limit=10),
            "settings_snapshot": request.app.state.settings.safe_settings_snapshot,
        }
    )
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        context,
    )


@router.get("/admin/communications", response_class=HTMLResponse)
def communications(
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
) -> HTMLResponse:
    service = CommunicationService()
    context = _base_context(
        request,
        active_page="communications",
        stats=service.summary_stats(db),
    )
    context.update({"records": service.list_records(db, limit=50)})
    return templates.TemplateResponse(
        request,
        "communications.html",
        context,
    )


@router.get("/admin/communications/{request_id}", response_class=HTMLResponse)
def communication_detail(
    request: Request, request_id: str, db: Annotated[Session, Depends(get_db_session)]
) -> HTMLResponse:
    service = CommunicationService()
    detail = CommunicationService().get_detail(db, request_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Communication not found")
    return templates.TemplateResponse(
        request,
        "communication_detail.html",
        {
            **_base_context(
                request,
                active_page="communications",
                stats=service.summary_stats(db),
            ),
            "detail": detail,
        },
    )


@router.get("/admin/review", response_class=HTMLResponse)
def review_queue(request: Request, db: Annotated[Session, Depends(get_db_session)]) -> HTMLResponse:
    service = CommunicationService()
    context = _base_context(request, active_page="review", stats=service.summary_stats(db))
    context.update(
        {
            "records": service.list_records(
                db,
                status=CommunicationStatus.review_needed.value,
                limit=50,
            ),
        }
    )
    return templates.TemplateResponse(
        request,
        "review_queue.html",
        context,
    )


@router.get("/admin/settings", response_class=HTMLResponse)
def settings_page(
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
) -> HTMLResponse:
    service = CommunicationService()
    return templates.TemplateResponse(
        request,
        "settings.html",
        {
            **_base_context(request, active_page="settings", stats=service.summary_stats(db)),
            "snapshot": request.app.state.settings.safe_settings_snapshot,
        },
    )


def _record_or_404(db: Session, request_id: str) -> CommunicationRequestRecord:
    record = CommunicationService().get_detail(db, request_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Communication not found")
    raw = db.query(CommunicationRequestRecord).filter_by(request_id=request_id).first()
    assert raw is not None
    return raw


@router.post("/admin/communications/{request_id}/approve")
def approve(
    request_id: str,
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
) -> RedirectResponse:
    service = CommunicationService()
    record = _record_or_404(db, request_id)
    service.transition(
        db,
        record,
        CommunicationStatus.approved,
        "approved",
        "Approved in admin UI.",
    )
    db.commit()
    if request.app.state.settings.worker_auto_run:
        request.app.state.worker_service.process_request_id(db, request_id)
    return RedirectResponse(
        url=f"/admin/communications/{request_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/admin/communications/{request_id}/retry")
def retry(
    request_id: str,
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
) -> RedirectResponse:
    service = CommunicationService()
    record = _record_or_404(db, request_id)
    if record.status == CommunicationStatus.failed.value:
        service.transition(
            db,
            record,
            CommunicationStatus.dropped,
            "dropped",
            "Dropped instead of retry from failed.",
        )
    else:
        record.retry_count += 1
        if record.status == CommunicationStatus.failed_retryable.value:
            service.transition(
                db,
                record,
                CommunicationStatus.processing,
                "retry",
                "Retry requested.",
            )
        elif record.status == CommunicationStatus.review_needed.value:
            service.transition(
                db,
                record,
                CommunicationStatus.approved,
                "retry_approved",
                "Retry promoted to approved.",
            )
        elif record.status == CommunicationStatus.received.value:
            service.transition(
                db,
                record,
                CommunicationStatus.processing,
                "retry",
                "Retry requested.",
            )
    db.commit()
    request.app.state.worker_service.process_request_id(db, request_id)
    return RedirectResponse(
        url=f"/admin/communications/{request_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


def _badge_class(kind: str, value: object) -> str:
    key = str(value or "").lower()
    mapping = {
        "status": {
            "completed": "badge badge-success",
            "review_needed": "badge badge-warning",
            "processing": "badge badge-info",
            "bitrix_syncing": "badge badge-info",
            "failed": "badge badge-danger",
            "failed_retryable": "badge badge-danger",
            "received": "badge badge-neutral",
            "duplicate": "badge badge-neutral",
            "dropped": "badge badge-muted",
            "approved": "badge badge-success",
            "summarized": "badge badge-info",
        },
        "priority": {
            "high": "badge badge-danger",
            "medium": "badge badge-warning",
            "low": "badge badge-neutral",
        },
        "risk": {
            "high": "badge badge-danger",
            "medium": "badge badge-warning",
            "low": "badge badge-success",
        },
    }
    return mapping.get(kind, {}).get(key, "badge badge-neutral")


def _base_context(
    request: Request,
    *,
    active_page: str,
    stats: dict[str, object] | None = None,
) -> dict[str, object]:
    settings = request.app.state.settings
    return {
        "active_page": active_page,
        "mode_label": f"{settings.app_mode.title()} Runtime",
        "ai_provider": settings.ai_provider,
        "bitrix_mode": settings.bitrix_mode,
        "write_guard": "live" if settings.allow_bitrix_write else "safe",
        "masking_status": "enabled" if settings.masking_enabled else "disabled",
        "nav_total": (stats or {}).get("total", 0),
        "nav_review": (stats or {}).get("review_needed", 0),
    }


@router.post("/admin/communications/{request_id}/drop")
def drop(request_id: str, db: Annotated[Session, Depends(get_db_session)]) -> RedirectResponse:
    service = CommunicationService()
    record = _record_or_404(db, request_id)
    current = CommunicationStatus(record.status)
    if current == CommunicationStatus.failed:
        service.transition(
            db,
            record,
            CommunicationStatus.dropped,
            "dropped",
            "Dropped in admin UI.",
        )
    elif current == CommunicationStatus.review_needed:
        service.transition(
            db,
            record,
            CommunicationStatus.dropped,
            "dropped",
            "Dropped in admin UI.",
        )
    elif current == CommunicationStatus.received:
        service.transition(
            db,
            record,
            CommunicationStatus.dropped,
            "dropped",
            "Dropped in admin UI.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status for drop",
        )
    db.commit()
    return RedirectResponse(
        url=f"/admin/communications/{request_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/admin/communications/{request_id}/reprocess-ai")
def reprocess_ai(
    request_id: str, request: Request, db: Annotated[Session, Depends(get_db_session)]
) -> RedirectResponse:
    record = _record_or_404(db, request_id)
    record.summary_result_json = None
    record.last_error = None
    record.retry_count = 0
    record.status = CommunicationStatus.received.value
    CommunicationService().add_log(
        db,
        record.request_id,
        None,
        CommunicationStatus.received,
        "reprocess_ai",
        "AI reprocessing requested.",
    )
    db.commit()
    request.app.state.worker_service.process_request_id(db, request_id)
    return RedirectResponse(
        url=f"/admin/communications/{request_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
