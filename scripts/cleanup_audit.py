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
        description="Audit whether Bitrix24 cleanup actually removed tasks and timeline comments."
    )
    parser.add_argument(
        "--artifact",
        required=True,
        help="Path to a JSON artifact produced by live validation scripts.",
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
    artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
    records = artifact.get("records", [])
    summary = {"checked": 0, "deleted_ok": 0, "still_present": 0, "errors": 0}

    with httpx.Client(timeout=settings.bitrix_timeout_seconds) as client:
        for record in records:
            scenario = record.get("scenario")
            deal_id = record.get("external_deal_id")
            comment_id = record.get("timeline_comment_id")
            task_id = record.get("task_id")
            scenario_result = {
                "scenario": scenario,
                "timeline_comment_deleted": None,
                "task_deleted": None,
            }
            if comment_id and deal_id:
                comment_list = _call(
                    client,
                    settings.bitrix_webhook_url,
                    "crm.timeline.comment.list",
                    {"ownerTypeId": 2, "ownerId": int(deal_id)},
                )
                if comment_list["ok"]:
                    comments = (comment_list["result"] or {}).get("result", [])
                    scenario_result["timeline_comment_deleted"] = all(
                        int(item.get("ID", 0)) != int(comment_id) for item in comments
                    )
                else:
                    scenario_result["timeline_comment_deleted"] = "error"
            if task_id:
                task_get = _call(
                    client,
                    settings.bitrix_webhook_url,
                    "tasks.task.get",
                    {"taskId": int(task_id)},
                )
                if task_get["ok"]:
                    task_result = (task_get["result"] or {}).get("result")
                    scenario_result["task_deleted"] = not bool(task_result)
                else:
                    error_text = str(task_get.get("error", "")).lower()
                    scenario_result["task_deleted"] = (
                        "not found" in error_text or "404" in error_text
                    )

            print(json.dumps(scenario_result, ensure_ascii=False, indent=2))
            summary["checked"] += 1
            if scenario_result["timeline_comment_deleted"] == "error":
                summary["errors"] += 1
            if scenario_result["task_deleted"] == "error":
                summary["errors"] += 1
            flags = [
                value
                for value in [
                    scenario_result["timeline_comment_deleted"],
                    scenario_result["task_deleted"],
                ]
                if value is not None
            ]
            if flags and all(flags):
                summary["deleted_ok"] += 1
            elif any(flag is False for flag in flags):
                summary["still_present"] += 1

    print("SUMMARY")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
