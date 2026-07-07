from __future__ import annotations

from app.services.bitrix_adapter import BitrixAdapter


class MockBitrixAdapter(BitrixAdapter):
    def __init__(self, allow_write: bool = False) -> None:
        self.allow_write = allow_write
        self.planned_actions: list[dict[str, object]] = []

    def test_connection(self) -> dict[str, object]:
        return {"ok": True, "mode": "mock"}

    def add_timeline_comment(self, external_deal_id: str | None, comment: str) -> dict[str, object]:
        action = {
            "action": "timeline_comment",
            "external_deal_id": external_deal_id,
            "comment": comment,
        }
        self.planned_actions.append(action)
        return {"ok": True, "dry_run": not self.allow_write, "planned_action": action}

    def create_task(
        self,
        external_deal_id: str | None,
        title: str,
        description: str,
        due_date: str | None,
        responsible_id: int | None,
    ) -> dict[str, object]:
        action = {
            "action": "create_task",
            "external_deal_id": external_deal_id,
            "title": title,
            "description": description,
            "due_date": due_date,
            "responsible_id": responsible_id,
        }
        self.planned_actions.append(action)
        return {"ok": True, "dry_run": not self.allow_write, "planned_action": action}
