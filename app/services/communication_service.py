from __future__ import annotations

import json

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.masking import mask_text
from app.models import CommunicationRequestRecord, ProcessingLogRecord
from app.schemas import (
    CommunicationCreate,
    CommunicationDetail,
    CommunicationStatus,
    PriorityLevel,
    ProcessingLogEntry,
    RiskLevel,
    SummaryResult,
)
from app.state_machine import validate_transition


class CommunicationService:
    def create_request(
        self,
        db: Session,
        payload: CommunicationCreate,
        *,
        masked_payload: dict[str, object],
    ) -> tuple[CommunicationRequestRecord, bool]:
        existing = db.scalar(
            select(CommunicationRequestRecord).where(
                CommunicationRequestRecord.idempotency_key == payload.idempotency_key
            )
        )
        if existing:
            return existing, True
        record = CommunicationRequestRecord(
            idempotency_key=payload.idempotency_key,
            source=payload.source,
            channel=payload.channel.value,
            external_deal_id=payload.external_deal_id,
            external_lead_id=payload.external_lead_id,
            client_name=mask_text(payload.client_name),
            client_contact=mask_text(payload.client_contact),
            communication_text=mask_text(payload.communication_text) or "",
            current_stage=payload.current_stage,
            manager_notes=mask_text(payload.manager_notes),
            status=CommunicationStatus.received.value,
            priority=PriorityLevel.medium.value,
            risk_level=RiskLevel.medium.value,
            masked_payload_json=json.dumps(masked_payload, ensure_ascii=False),
        )
        db.add(record)
        db.flush()
        self.add_log(
            db,
            record.request_id,
            None,
            CommunicationStatus.received,
            "received",
            "Request accepted.",
        )
        db.commit()
        db.refresh(record)
        return record, False

    def add_log(
        self,
        db: Session,
        request_id: str,
        from_status: CommunicationStatus | None,
        to_status: CommunicationStatus,
        event_type: str,
        message: str,
        metadata: dict[str, object] | None = None,
    ) -> None:
        db.add(
            ProcessingLogRecord(
                request_id=request_id,
                event_type=event_type,
                from_status=from_status.value if from_status else None,
                to_status=to_status.value,
                message=message,
                metadata_json=json.dumps(metadata or {}, ensure_ascii=False),
            )
        )

    def transition(
        self,
        db: Session,
        record: CommunicationRequestRecord,
        to_status: CommunicationStatus,
        event_type: str,
        message: str,
        metadata: dict[str, object] | None = None,
    ) -> None:
        current = CommunicationStatus(record.status)
        validate_transition(current, to_status)
        record.status = to_status.value
        self.add_log(db, record.request_id, current, to_status, event_type, message, metadata)
        db.flush()

    def update_summary(
        self,
        db: Session,
        record: CommunicationRequestRecord,
        summary: SummaryResult,
    ) -> None:
        record.summary_result_json = summary.model_dump_json()
        record.priority = summary.priority.value
        record.risk_level = summary.risk_level.value
        db.flush()

    def get_detail(self, db: Session, request_id: str) -> CommunicationDetail | None:
        record = db.scalar(
            select(CommunicationRequestRecord).where(
                CommunicationRequestRecord.request_id == request_id
            )
        )
        if record is None:
            return None
        logs = db.scalars(
            select(ProcessingLogRecord)
            .where(ProcessingLogRecord.request_id == request_id)
            .order_by(ProcessingLogRecord.created_at.asc(), ProcessingLogRecord.id.asc())
        ).all()
        detail = CommunicationDetail(
            request_id=record.request_id,
            idempotency_key=record.idempotency_key,
            source=record.source,
            channel=record.channel,
            external_deal_id=record.external_deal_id,
            external_lead_id=record.external_lead_id,
            client_name=record.client_name,
            client_contact=record.client_contact,
            communication_text=record.communication_text,
            current_stage=record.current_stage,
            manager_notes=record.manager_notes,
            status=record.status,
            priority=record.priority,
            risk_level=record.risk_level,
            retry_count=record.retry_count,
            last_error=record.last_error,
            summary_result=SummaryResult.model_validate_json(record.summary_result_json)
            if record.summary_result_json
            else None,
            masked_payload=json.loads(record.masked_payload_json or "{}"),
            created_at=record.created_at,
            updated_at=record.updated_at,
            logs=[
                ProcessingLogEntry(
                    event_type=log.event_type,
                    from_status=log.from_status,
                    to_status=log.to_status,
                    message=log.message,
                    metadata=json.loads(log.metadata_json or "{}"),
                    created_at=log.created_at,
                )
                for log in logs
            ],
        )
        return detail

    def list_records(
        self,
        db: Session,
        *,
        status: str | None = None,
        limit: int = 50,
    ) -> list[CommunicationRequestRecord]:
        query = select(CommunicationRequestRecord)
        if status:
            query = query.where(CommunicationRequestRecord.status == status)
        query = query.order_by(desc(CommunicationRequestRecord.created_at)).limit(limit)
        return list(db.scalars(query).all())

    def summary_stats(self, db: Session) -> dict[str, object]:
        total = db.scalar(select(func.count()).select_from(CommunicationRequestRecord)) or 0
        review_needed = db.scalar(
            select(func.count())
            .select_from(CommunicationRequestRecord)
            .where(CommunicationRequestRecord.status == CommunicationStatus.review_needed.value)
        ) or 0
        failed = db.scalar(
            select(func.count())
            .select_from(CommunicationRequestRecord)
            .where(
                CommunicationRequestRecord.status.in_(
                    [
                        CommunicationStatus.failed.value,
                        CommunicationStatus.failed_retryable.value,
                    ]
                )
            )
        ) or 0
        by_status_rows = db.execute(
            select(CommunicationRequestRecord.status, func.count()).group_by(
                CommunicationRequestRecord.status
            )
        ).all()
        by_priority_rows = db.execute(
            select(CommunicationRequestRecord.priority, func.count()).group_by(
                CommunicationRequestRecord.priority
            )
        ).all()
        by_channel_rows = db.execute(
            select(CommunicationRequestRecord.channel, func.count()).group_by(
                CommunicationRequestRecord.channel
            )
        ).all()
        completed = db.scalar(
            select(func.count())
            .select_from(CommunicationRequestRecord)
            .where(CommunicationRequestRecord.status == CommunicationStatus.completed.value)
        ) or 0
        high_risk = db.scalar(
            select(func.count())
            .select_from(CommunicationRequestRecord)
            .where(CommunicationRequestRecord.risk_level == RiskLevel.high.value)
        ) or 0
        return {
            "total": total,
            "review_needed": review_needed,
            "failed": failed,
            "completed": completed,
            "high_risk": high_risk,
            "by_status": {status: count for status, count in by_status_rows},
            "by_priority": {priority: count for priority, count in by_priority_rows if priority},
            "by_channel": {channel: count for channel, count in by_channel_rows if channel},
        }
