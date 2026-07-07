from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.masking import mask_text
from app.schemas import (
    CommunicationCreate,
    CommunicationDetail,
    CommunicationStatus,
    CommunicationSubmitResponse,
)
from app.security import require_admin_auth, verify_webhook_secret
from app.services.communication_service import CommunicationService

router = APIRouter(prefix="/api/v1/communications", tags=["communications"])


@router.post("", response_model=CommunicationSubmitResponse)
def create_communication(
    payload: CommunicationCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
) -> CommunicationSubmitResponse:
    verify_webhook_secret(request)
    limiter = request.app.state.rate_limiter
    if not limiter.allow("communications"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
    service = CommunicationService()
    masked_payload = {
        key: mask_text(str(value)) if isinstance(value, str) else value
        for key, value in payload.model_dump(mode="python").items()
    }
    record, is_duplicate = service.create_request(db, payload, masked_payload=masked_payload)
    if is_duplicate:
        return CommunicationSubmitResponse(
            request_id=record.request_id,
            status=CommunicationStatus.duplicate,
            message="Duplicate idempotency_key",
        )
    if request.app.state.settings.worker_auto_run:
        request.app.state.worker_service.process_request_id(db, record.request_id)
        db.refresh(record)
    return CommunicationSubmitResponse(
        request_id=record.request_id,
        status=CommunicationStatus(record.status),
    )


@router.get("/{request_id}", response_model=CommunicationDetail)
def get_communication(
    request_id: str,
    request: Request,
    db: Annotated[Session, Depends(get_db_session)],
) -> CommunicationDetail:
    if request.headers.get("X-Webhook-Secret"):
        verify_webhook_secret(request)
    else:
        require_admin_auth(request)
    detail = CommunicationService().get_detail(db, request_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Communication not found")
    return detail
