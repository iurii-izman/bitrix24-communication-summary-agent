from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CommunicationRequestRecord
from app.schemas import CommunicationCreate, CommunicationStatus, SummaryResult
from app.services.bitrix_mock import MockBitrixAdapter
from app.services.bitrix_real import RealBitrixAdapter
from app.services.communication_service import CommunicationService
from app.services.deterministic_fallback import DeterministicFallback
from app.services.mock_ai_provider import MockCommunicationAIProvider
from app.services.openai_provider import OpenAICommunicationProvider
from app.services.routing import RoutingService
from app.services.task_builder import build_consolidated_task
from app.settings import Settings


class WorkerService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.communication_service = CommunicationService()
        self.routing_service = RoutingService(settings)
        self.fallback = DeterministicFallback()
        self.bitrix_adapter = (
            MockBitrixAdapter(settings.allow_bitrix_write)
            if settings.bitrix_mode == "mock"
            else RealBitrixAdapter(settings)
        )

    def process_request_id(self, db: Session, request_id: str) -> CommunicationRequestRecord:
        record = db.scalar(
            select(CommunicationRequestRecord).where(
                CommunicationRequestRecord.request_id == request_id
            )
        )
        if record is None:
            raise ValueError("Request not found")
        return self.process_record(db, record)

    def process_record(
        self,
        db: Session,
        record: CommunicationRequestRecord,
    ) -> CommunicationRequestRecord:
        if record.status not in {
            CommunicationStatus.received.value,
            CommunicationStatus.failed_retryable.value,
            CommunicationStatus.approved.value,
            CommunicationStatus.processing.value,
        }:
            return record

        payload = CommunicationCreate(
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
        )

        if record.status not in {
            CommunicationStatus.approved.value,
            CommunicationStatus.processing.value,
        }:
            self.communication_service.transition(
                db,
                record,
                CommunicationStatus.processing,
                "processing_started",
                "Worker started processing the communication.",
            )
            summary = self._summarize(payload)
            self.communication_service.update_summary(db, record, summary)
            self.communication_service.transition(
                db,
                record,
                CommunicationStatus.summarized,
                "summarized",
                "Structured summary generated.",
                {"confidence": summary.confidence, "model_used": summary.model_used},
            )
            decision = self.routing_service.decide(payload, summary)
            if decision.decision == "drop":
                self.communication_service.transition(
                    db, record, CommunicationStatus.dropped, "dropped", decision.reason
                )
                db.commit()
                db.refresh(record)
                return record
            if decision.decision == "review_needed":
                self.communication_service.transition(
                    db,
                    record,
                    CommunicationStatus.review_needed,
                    "review_needed",
                    decision.reason,
                    {"required_human_review": decision.required_human_review},
                )
                db.commit()
                db.refresh(record)
                return record
        summary = SummaryResult.model_validate_json(
            record.summary_result_json
            or self.fallback.summarize(payload).model_dump_json()
        )
        self.communication_service.transition(
            db,
            record,
            CommunicationStatus.bitrix_syncing,
            "bitrix_syncing",
            "Preparing Bitrix24 timeline comment and task.",
        )
        task = build_consolidated_task(summary, self.settings.bitrix_responsible_id)
        timeline_result = self.bitrix_adapter.add_timeline_comment(
            record.external_deal_id,
            summary.timeline_comment,
        )
        task_result = self.bitrix_adapter.create_task(
            record.external_deal_id,
            task.title,
            task.description,
            task.due_date.isoformat() if task.due_date else None,
            task.responsible_id,
        )
        self.communication_service.add_log(
            db,
            record.request_id,
            CommunicationStatus.bitrix_syncing,
            CommunicationStatus.bitrix_syncing,
            "bitrix_actions_planned",
            "Bitrix actions prepared.",
            {"timeline": timeline_result, "task": task_result},
        )
        self.communication_service.transition(
            db, record, CommunicationStatus.completed, "completed", "Processing completed."
        )
        record.last_error = None
        db.commit()
        db.refresh(record)
        return record

    def _summarize(self, payload: CommunicationCreate) -> SummaryResult:
        try:
            if self.settings.ai_provider == "openai":
                return OpenAICommunicationProvider(self.settings).summarize(payload)
            return MockCommunicationAIProvider(
                self.settings.review_confidence_threshold
            ).summarize(payload)
        except Exception:  # noqa: BLE001
            return self.fallback.summarize(payload)
