from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import CommunicationRequestRecord


def test_same_idempotency_key_returns_duplicate(client, auth_headers, settings) -> None:
    payload = {
        "idempotency_key": "dup-1",
        "source": "manual",
        "channel": "email",
        "communication_text": "Client asked for CRM pricing and timeline.",
    }
    first = client.post("/api/v1/communications", headers=auth_headers, json=payload)
    second = client.post("/api/v1/communications", headers=auth_headers, json=payload)
    assert first.status_code == 200
    assert second.json()["status"] == "duplicate"

    engine = create_engine(
        settings.database_url,
        future=True,
        connect_args={"check_same_thread": False},
    )
    with Session(engine) as session:
        rows = session.scalars(select(CommunicationRequestRecord)).all()
    assert len(rows) == 1
