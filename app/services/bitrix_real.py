from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from app.masking import sanitize_error
from app.services.bitrix_adapter import BitrixAdapter
from app.settings import Settings


class RealBitrixAdapter(BitrixAdapter):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def test_connection(self) -> dict[str, object]:
        if not self.settings.bitrix_webhook_url:
            return {"ok": False, "error": "Bitrix webhook is not configured."}
        return {"ok": True, "mode": "real-boundary"}

    def add_timeline_comment(self, external_deal_id: str | None, comment: str) -> dict[str, object]:
        payload = {
            "fields": {
                "ENTITY_ID": int(external_deal_id) if external_deal_id else None,
                "ENTITY_TYPE": "deal",
                "COMMENT": comment,
            }
        }
        return self._call("crm.timeline.comment.add", payload)

    def create_task(
        self,
        external_deal_id: str | None,
        title: str,
        description: str,
        due_date: str | None,
        responsible_id: int | None,
    ) -> dict[str, object]:
        payload = {
            "fields": {
                "TITLE": title,
                "DESCRIPTION": description,
                "DEADLINE": due_date,
                "RESPONSIBLE_ID": responsible_id or self.settings.bitrix_responsible_id,
                "UF_CRM_TASK": [f"D_{external_deal_id}"] if external_deal_id else [],
            }
        }
        return self._call("tasks.task.add", payload)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def _call(self, method: str, payload: dict[str, object]) -> dict[str, object]:
        if not self.settings.allow_bitrix_write:
            return {
                "ok": True,
                "dry_run": True,
                "planned_action": {"method": method, "payload": payload},
            }
        if not self.settings.bitrix_webhook_url:
            return {"ok": False, "error": "Bitrix webhook is not configured."}
        url = self.settings.bitrix_webhook_url.rstrip("/") + f"/{method}.json"
        try:
            with httpx.Client(timeout=self.settings.bitrix_timeout_seconds) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                return {"ok": True, "dry_run": False, "result": response.json()}
        except httpx.HTTPError as exc:
            return {"ok": False, "error": sanitize_error(str(exc))}
