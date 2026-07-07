# ruff: noqa: E402

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.settings import Settings

ARTIFACTS_DIR = ROOT_DIR / "runtime_artifacts" / "bitrix_validation"


def build_runtime_settings(*, enable_write: bool, real_mode: bool = True) -> Settings:
    env_settings = Settings()
    return Settings(
        app_name=env_settings.app_name,
        app_mode=env_settings.app_mode,
        database_url=env_settings.database_url,
        webhook_secret=env_settings.webhook_secret,
        admin_username=env_settings.admin_username,
        admin_password=env_settings.admin_password,
        ai_provider=env_settings.ai_provider,
        openai_api_key=env_settings.openai_api_key,
        openai_model=env_settings.openai_model,
        bitrix_mode="real" if real_mode else env_settings.bitrix_mode,
        bitrix_crm_mode=env_settings.bitrix_crm_mode,
        bitrix_webhook_url=env_settings.bitrix_webhook_url,
        bitrix_responsible_id=env_settings.bitrix_responsible_id,
        allow_bitrix_write=enable_write,
        masking_enabled=env_settings.masking_enabled,
        worker_auto_run=env_settings.worker_auto_run,
        review_confidence_threshold=env_settings.review_confidence_threshold,
        rate_limit_window_seconds=env_settings.rate_limit_window_seconds,
        rate_limit_max_requests=env_settings.rate_limit_max_requests,
        provider_timeout_seconds=env_settings.provider_timeout_seconds,
        bitrix_timeout_seconds=env_settings.bitrix_timeout_seconds,
        max_retry_count=env_settings.max_retry_count,
        short_text_drop_threshold=env_settings.short_text_drop_threshold,
        app_debug=env_settings.app_debug,
    )


def scenario_payloads(deal_id: str, *, batch_key: str) -> list[tuple[str, dict[str, object]]]:
    return [
        (
            "live_completed_a",
            {
                "idempotency_key": f"live-completed-a-{batch_key}",
                "source": "manual",
                "channel": "email",
                "external_deal_id": deal_id,
                "client_name": "Validation Client A",
                "client_contact": "+37300007777",
                "communication_text": (
                    "Client needs Bitrix24 implementation with 1C integration. "
                    "Budget approved at 18000 EUR. Decision maker is CEO. "
                    "Asked for a proposal and follow-up call on Friday."
                ),
                "current_stage": "proposal",
                "manager_notes": "Live validation scenario A",
            },
        ),
        (
            "live_completed_b",
            {
                "idempotency_key": f"live-completed-b-{batch_key}",
                "source": "manual",
                "channel": "call_transcript",
                "external_deal_id": deal_id,
                "client_name": "Validation Client B",
                "client_contact": "validation-b@example.test",
                "communication_text": (
                    "Client wants CRM audit and Bitrix24 implementation scope. "
                    "Budget confirmed. Decision maker is founder. "
                    "Follow-up call planned for Friday."
                ),
                "current_stage": "qualification",
                "manager_notes": "Live validation scenario B",
            },
        ),
        (
            "review_needed_case",
            {
                "idempotency_key": f"live-review-{batch_key}",
                "source": "manual",
                "channel": "chat",
                "external_deal_id": deal_id,
                "client_name": "Validation Client Review",
                "client_contact": "+37300008888",
                "communication_text": "call me later",
                "current_stage": "new",
                "manager_notes": "Should stay in review queue.",
            },
        ),
    ]


def extract_bitrix_refs(detail: dict[str, Any]) -> dict[str, Any]:
    logs = detail.get("logs", [])
    bitrix_log = next(
        (entry for entry in logs if entry["event_type"] == "bitrix_actions_planned"),
        None,
    )
    if not bitrix_log:
        return {
            "timeline_comment_id": None,
            "task_id": None,
            "bitrix_actions": None,
        }

    metadata = bitrix_log.get("metadata") or {}
    timeline_meta = metadata.get("timeline") or {}
    task_meta = metadata.get("task") or {}
    timeline_result = (((timeline_meta.get("result") or {}).get("result")))
    task_result = (
        (((task_meta.get("result") or {}).get("result") or {}).get("task") or {}).get("id")
    )
    task_id = (
        int(task_result)
        if isinstance(task_result, str | int) and str(task_result).isdigit()
        else None
    )
    return {
        "timeline_comment_id": timeline_result if isinstance(timeline_result, int) else None,
        "task_id": task_id,
        "bitrix_actions": metadata,
    }


def build_artifact_record(
    *,
    scenario: str,
    detail: dict[str, Any],
    write_enabled: bool,
) -> dict[str, Any]:
    refs = extract_bitrix_refs(detail)
    return {
        "scenario": scenario,
        "request_id": detail.get("request_id"),
        "status": detail.get("status"),
        "external_deal_id": detail.get("external_deal_id"),
        "priority": detail.get("priority"),
        "risk_level": detail.get("risk_level"),
        "write_enabled": write_enabled,
        "timeline_comment_id": refs["timeline_comment_id"],
        "task_id": refs["task_id"],
        "bitrix_actions": refs["bitrix_actions"],
    }


def write_artifact(*, name_prefix: str, payload: dict[str, Any]) -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = ARTIFACTS_DIR / f"{name_prefix}_{stamp}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
