# ruff: noqa: E402

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import create_engine_from_settings, create_session_factory, init_db
from app.schemas import CommunicationCreate
from app.services.communication_service import CommunicationService
from app.settings import Settings


def main() -> None:
    settings = Settings()
    engine = create_engine_from_settings(settings)
    init_db(engine)
    session_factory = create_session_factory(engine)
    service = CommunicationService()
    samples_path = ROOT_DIR / "demo_data" / "sample_communications.json"
    payloads = json.loads(samples_path.read_text(encoding="utf-8"))
    with session_factory() as db:
        for raw in payloads:
            payload = CommunicationCreate.model_validate(raw)
            masked_payload = payload.model_dump(mode="json")
            service.create_request(db, payload, masked_payload=masked_payload)
    print(f"Seeded demo data from {samples_path}")


if __name__ == "__main__":
    main()
