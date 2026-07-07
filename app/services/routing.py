from __future__ import annotations

from pathlib import Path

import yaml

from app.schemas import Channel, CommunicationCreate, RiskLevel, RoutingDecision, SummaryResult
from app.settings import Settings


class RoutingService:
    def __init__(self, settings: Settings, rules_path: Path | None = None) -> None:
        self.settings = settings
        self.rules_path = (
            rules_path
            or Path(__file__).resolve().parents[2] / "config" / "routing_rules.yaml"
        )
        self.rules = yaml.safe_load(self.rules_path.read_text(encoding="utf-8"))

    def decide(self, payload: CommunicationCreate, summary: SummaryResult) -> RoutingDecision:
        if summary.confidence < self.settings.review_confidence_threshold:
            return RoutingDecision(
                decision="review_needed",
                reason="Confidence below review threshold.",
                required_human_review=True,
            )
        if summary.risk_level == RiskLevel.high:
            return RoutingDecision(
                decision="review_needed",
                reason="High risk communication requires human review.",
                required_human_review=True,
            )
        if {"budget", "decision_maker"} & set(summary.missing_info):
            return RoutingDecision(
                decision="review_needed",
                reason="Critical missing information requires manual review.",
                required_human_review=True,
            )
        if len(payload.communication_text.split()) <= self.settings.short_text_drop_threshold:
            return RoutingDecision(
                decision="drop",
                reason="Communication is too short for meaningful autonomous action.",
                required_human_review=False,
            )
        if payload.channel not in set(Channel):
            return RoutingDecision(
                decision="review_needed",
                reason="Unknown channel requires manual review.",
                required_human_review=True,
            )
        return RoutingDecision(
            decision="proceed",
            reason="Ready for Bitrix sync.",
            required_human_review=False,
        )
