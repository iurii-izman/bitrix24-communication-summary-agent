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
        description="Run batch Bitrix24 validation across multiple deal IDs."
    )
    parser.add_argument(
        "--deal-ids",
        required=True,
        help="Comma-separated Bitrix24 deal IDs, for example 1,2,3",
    )
    parser.add_argument(
        "--enable-write",
        action="store_true",
        help="Enable real Bitrix24 write calls for this one batch execution.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = build_runtime_settings(enable_write=args.enable_write)
    deal_ids = [item.strip() for item in args.deal_ids.split(",") if item.strip()]
    if not deal_ids:
        raise SystemExit("No valid deal IDs were provided.")

    batch_key = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    artifact_records: list[dict[str, object]] = []
    with TestClient(create_app(settings)) as client:
        health = client.get("/health")
        print("HEALTH", health.status_code, health.json())
        for index, deal_id in enumerate(deal_ids, start=1):
            for label, payload in scenario_payloads(deal_id, batch_key=f"{batch_key}-{index}"):
                scenario_label = f"deal_{deal_id}:{label}"
                created = client.post(
                    "/api/v1/communications",
                    headers={"X-Webhook-Secret": settings.webhook_secret},
                    json=payload,
                )
                print("CREATE", scenario_label, created.status_code, created.json())
                request_id = created.json()["request_id"]
                detail = client.get(
                    f"/api/v1/communications/{request_id}",
                    headers={"X-Webhook-Secret": settings.webhook_secret},
                )
                record = build_artifact_record(
                    scenario=scenario_label,
                    detail=detail.json(),
                    write_enabled=args.enable_write,
                )
                artifact_records.append(record)
                print(json.dumps(record, ensure_ascii=False, indent=2))
    artifact_path = write_artifact(
        name_prefix="batch_live_validation",
        payload={
            "validated_at": datetime.now(UTC).isoformat(),
            "write_enabled": args.enable_write,
            "deal_ids": deal_ids,
            "records": artifact_records,
        },
    )
    print("ARTIFACT", artifact_path)


if __name__ == "__main__":
    main()
