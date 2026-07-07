from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import CommunicationCreate, SummaryResult


class CommunicationAIProvider(ABC):
    @abstractmethod
    def summarize(self, payload: CommunicationCreate) -> SummaryResult:
        raise NotImplementedError
