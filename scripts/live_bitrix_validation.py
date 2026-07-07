# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient

from app.main import create_app
from scripts._bitrix_validation_common import (
    build_artifact_record,
    build_runtime_settings,
    scenario_payloads,
    write_artifact,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run controlled Bitrix24 validation scenarios "
            "against the current .env settings."
        )
    )
    parser.add_argument(
        "--deal-id",
        default="1",
        help="Bitrix24 deal ID used for live sync scenarios.",
    )
    parser.add_argument(
        "--enable-write",
        action="store_true",
        help="Enable real Bitrix24 write calls for this one script execution.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = build_runtime_settings(enable_write=args.enable_write)
    if not settings.bitrix_webhook_url:
        raise SystemExit("BITRIX_WEBHOOK_URL is missing in .env")

    batch_key = "single-" + args.deal_id
    artifact_records: list[dict[str, object]] = []
    with TestClient(create_app(settings)) as client:
        health = client.get("/health")
        print("HEALTH", health.status_code, health.json())
        for label, payload in scenario_payloads(args.deal_id, batch_key=batch_key):
            created = client.post(
                "/api/v1/communications",
                headers={"X-Webhook-Secret": settings.webhook_secret},
                json=payload,
            )
            print("CREATE", label, created.status_code, created.json())
            request_id = created.json()["request_id"]
            detail = client.get(
                f"/api/v1/communications/{request_id}",
                headers={"X-Webhook-Secret": settings.webhook_secret},
            )
            detail_json = detail.json()
            record = build_artifact_record(
                scenario=label,
                detail=detail_json,
                write_enabled=args.enable_write,
            )
            artifact_records.append(record)
            print(f"SCENARIO {label}")
            print(json.dumps(record, ensure_ascii=False, indent=2))
    artifact_path = write_artifact(
        name_prefix="live_validation",
        payload={
            "validated_at": datetime.now(UTC).isoformat(),
            "write_enabled": args.enable_write,
            "deal_ids": [args.deal_id],
            "records": artifact_records,
        },
    )
    print("ARTIFACT", artifact_path)


if __name__ == "__main__":
    main()
