# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.masking import sanitize_error
from app.settings import Settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Delete Bitrix24 timeline comments and tasks using a validation artifact."
    )
    parser.add_argument(
        "--artifact",
        required=True,
        help=(
            "Path to a JSON artifact produced by "
            "live_bitrix_validation.py or batch_live_validation.py"
        ),
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Actually perform deletions. Without this flag the script runs "
            "in dry-run preview mode."
        ),
    )
    return parser


def _call(
    client: httpx.Client,
    webhook_url: str,
    method: str,
    payload: dict[str, object],
) -> dict[str, object]:
    url = webhook_url.rstrip("/") + f"/{method}.json"
    try:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("error"):
            return {
                "ok": False,
                "error": sanitize_error(str(data.get("error_description") or data["error"])),
            }
        return {"ok": True, "result": data}
    except httpx.HTTPError as exc:
        return {"ok": False, "error": sanitize_error(str(exc))}


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings()
    if not settings.bitrix_webhook_url:
        raise SystemExit("BITRIX_WEBHOOK_URL is missing in .env")

    artifact_path = Path(args.artifact)
    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    records = data.get("records", [])
    with httpx.Client(timeout=settings.bitrix_timeout_seconds) as client:
        for record in records:
            scenario = record.get("scenario")
            deal_id = record.get("external_deal_id")
            comment_id = record.get("timeline_comment_id")
            task_id = record.get("task_id")
            print(f"SCENARIO {scenario}")
            if not args.execute:
                print(
                    json.dumps(
                        {
                            "dry_run": True,
                            "timeline_comment_id": comment_id,
                            "task_id": task_id,
                            "external_deal_id": deal_id,
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
                continue

            if comment_id and deal_id:
                comment_result = _call(
                    client,
                    settings.bitrix_webhook_url,
                    "crm.timeline.comment.delete",
                    {"id": comment_id, "ownerTypeId": 2, "ownerId": int(deal_id)},
                )
                print("TIMELINE_DELETE", json.dumps(comment_result, ensure_ascii=False))
            if task_id:
                task_result = _call(
                    client,
                    settings.bitrix_webhook_url,
                    "tasks.task.delete",
                    {"taskId": int(task_id)},
                )
                print("TASK_DELETE", json.dumps(task_result, ensure_ascii=False))


if __name__ == "__main__":
    main()
