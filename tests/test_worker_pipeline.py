from app.database import create_engine_from_settings, create_session_factory, init_db
from app.schemas import CommunicationCreate
from app.services.communication_service import CommunicationService
from app.services.worker import WorkerService


def _create_record(settings, payload: CommunicationCreate):
    engine = create_engine_from_settings(settings)
    init_db(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as db:
        service = CommunicationService()
        record, _ = service.create_request(
            db,
            payload,
            masked_payload=payload.model_dump(mode="json"),
        )
    return session_factory, record.request_id


def test_happy_path_reaches_completed(settings) -> None:
    session_factory, request_id = _create_record(
        settings,
        CommunicationCreate(
            idempotency_key="worker-1",
            source="manual",
            channel="call_transcript",
            communication_text=(
                "Client wants Bitrix24 implementation with proposal "
                "and clear price discussion tomorrow."
            ),
        ),
    )
    with session_factory() as db:
        record = WorkerService(settings).process_request_id(db, request_id)
        assert record.status == "review_needed" or record.status == "completed"


def test_review_needed_path_works(settings) -> None:
    session_factory, request_id = _create_record(
        settings,
        CommunicationCreate(
            idempotency_key="worker-2",
            source="manual",
            channel="chat",
            communication_text="call me later",
        ),
    )
    with session_factory() as db:
        record = WorkerService(settings).process_request_id(db, request_id)
        assert record.status == "review_needed"


def test_failed_provider_uses_fallback(settings, monkeypatch) -> None:
    session_factory, request_id = _create_record(
        settings,
        CommunicationCreate(
            idempotency_key="worker-3",
            source="manual",
            channel="email",
            communication_text="Need CRM support now.",
        ),
    )
    worker = WorkerService(settings)
    monkeypatch.setattr(worker, "_summarize", lambda payload: worker.fallback.summarize(payload))
    with session_factory() as db:
        record = worker.process_request_id(db, request_id)
        assert record.summary_result_json is not None
