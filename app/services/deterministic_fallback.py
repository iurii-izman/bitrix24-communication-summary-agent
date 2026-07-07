from __future__ import annotations

from datetime import date, timedelta

from app.schemas import (
    CommunicationCreate,
    FollowUp,
    NextStep,
    PriorityLevel,
    RecommendedTask,
    RiskLevel,
    Sentiment,
    SummaryResult,
)
from app.services.timeline_formatter import format_timeline_comment


class DeterministicFallback:
    def summarize(self, payload: CommunicationCreate) -> SummaryResult:
        summary = SummaryResult(
            summary=(
                "Conservative fallback summary generated because the primary "
                "AI provider was unavailable."
            ),
            client_intent="Clarify request details and confirm next follow-up manually.",
            sentiment=Sentiment.unknown,
            priority=PriorityLevel.medium,
            risk_level=RiskLevel.medium,
            agreements=[],
            risks=["Primary AI provider failed; manual review is required before CRM sync."],
            missing_info=["budget", "decision_maker"],
            next_steps=[
                NextStep(
                    title="Review communication manually",
                    owner="manager",
                    due_date=date.today() + timedelta(days=1),
                    rationale="Fallback output must be confirmed by a human.",
                )
            ],
            follow_up=FollowUp(
                needed=True,
                date=date.today() + timedelta(days=1),
                reason="Confirm the request manually because AI fallback was used.",
            ),
            recommended_tasks=[
                RecommendedTask(
                    title="Manual review required",
                    description=f"Validate communication: {payload.communication_text[:180]}",
                    priority=PriorityLevel.high,
                    due_date=date.today() + timedelta(days=1),
                )
            ],
            timeline_comment="",
            draft_reply=(
                "Draft only: thank the client, confirm receipt, and promise a "
                "manual follow-up."
            ),
            confidence=0.35,
            review_reason="Fallback provider used after AI failure.",
            human_approval_required=True,
            model_used="deterministic-fallback",
        )
        summary.timeline_comment = format_timeline_comment(summary)
        return summary
