from __future__ import annotations

from abc import ABC, abstractmethod


class BitrixAdapter(ABC):
    @abstractmethod
    def test_connection(self) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def add_timeline_comment(self, external_deal_id: str | None, comment: str) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def create_task(
        self,
        external_deal_id: str | None,
        title: str,
        description: str,
        due_date: str | None,
        responsible_id: int | None,
    ) -> dict[str, object]:
        raise NotImplementedError
