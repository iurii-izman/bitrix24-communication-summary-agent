# ruff: noqa: E402

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import Settings


def main() -> None:
    db_path = ROOT_DIR / "smoke.sqlite3"
    settings = Settings(database_url=f"sqlite+pysqlite:///{db_path}", worker_auto_run=True)
    with TestClient(create_app(settings)) as client:
        health = client.get("/health")
        print("/health", health.status_code, health.json())
        payload = {
            "idempotency_key": "smoke-0001",
            "source": "manual",
            "channel": "call_transcript",
            "external_deal_id": "900",
            "client_name": "Smoke Client",
            "client_contact": "+37300009999",
            "communication_text": (
                "Client asked for Bitrix24 implementation with proposal "
                "and callback Friday."
            ),
            "current_stage": "qualification",
            "manager_notes": "Smoke flow",
        }
        created = client.post(
            "/api/v1/communications",
            headers={"X-Webhook-Secret": settings.webhook_secret},
            json=payload,
        )
        print("create", created.status_code, created.json())
        request_id = created.json()["request_id"]
        detail = client.get(
            f"/api/v1/communications/{request_id}",
            headers={"X-Webhook-Secret": settings.webhook_secret},
        )
        print("detail", detail.status_code)
        print(json.dumps(detail.json(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
