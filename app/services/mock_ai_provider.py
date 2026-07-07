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
from app.services.ai_provider import CommunicationAIProvider
from app.services.timeline_formatter import format_timeline_comment


class MockCommunicationAIProvider(CommunicationAIProvider):
    def __init__(self, confidence_threshold: float) -> None:
        self.confidence_threshold = confidence_threshold

    def summarize(self, payload: CommunicationCreate) -> SummaryResult:
        text = payload.communication_text.lower()
        priority = PriorityLevel.low
        risk_level = RiskLevel.low
        sentiment = Sentiment.neutral
        confidence = 0.88
        agreements: list[str] = []
        risks: list[str] = []
        missing_info: list[str] = []
        next_steps: list[NextStep] = []
        recommended_tasks: list[RecommendedTask] = []
        review_reason = None

        if any(
            keyword in text
            for keyword in ["bitrix24", "crm", "1c", "1с", "proposal", "commercial offer"]
        ):
            priority = PriorityLevel.high if "1c" in text or "1с" in text else PriorityLevel.medium
            agreements.append("Client expects structured CRM follow-up.")
        if "budget" not in text and "price" not in text and "cost" not in text:
            missing_info.append("budget")
        if "decision maker" not in text and "ceo" not in text and "owner" not in text:
            missing_info.append("decision_maker")
        if "friday" in text or "follow-up" in text or "call back" in text:
            next_steps.append(
                NextStep(
                    title="Schedule follow-up call",
                    owner="sales manager",
                    due_date=date.today() + timedelta(days=3),
                    rationale="The communication explicitly asked for a follow-up.",
                )
            )
        if "integration" in text or "1c" in text or "1с" in text:
            risks.append("Integration scope and field mapping must be validated.")
            risk_level = RiskLevel.medium
        if "delay" in text or "urgent" in text or "unhappy" in text or "who is responsible" in text:
            risk_level = RiskLevel.high
            sentiment = Sentiment.negative
            risks.append("Escalation risk due to dissatisfaction or urgency.")
        if "call me later" in text or len(payload.communication_text.split()) <= 3:
            confidence = 0.42
            review_reason = "Communication is too vague for safe autonomous action."
        if "asked to send proposal" in text or "commercial proposal" in text:
            agreements.append("Client asked for a proposal.")
        if "timeline" in text:
            agreements.append("Client asked for implementation timing.")

        if risk_level == RiskLevel.high and sentiment == Sentiment.neutral:
            sentiment = Sentiment.mixed

        if not next_steps:
            next_steps.append(
                NextStep(
                    title="Clarify scope and missing details",
                    owner="sales manager",
                    due_date=date.today() + timedelta(days=2),
                    rationale="Communication summary requires actionable clarification.",
                )
            )

        recommended_tasks.append(
            RecommendedTask(
                title="Prepare follow-up on communication",
                description="Review summary, confirm missing info, and respond with next steps.",
                priority=priority,
                due_date=next_steps[0].due_date,
            )
        )

        human_approval_required = (
            confidence < self.confidence_threshold or risk_level == RiskLevel.high
        )
        result = SummaryResult(
            summary=payload.communication_text[:280],
            client_intent="Client expects follow-up related to CRM / implementation needs.",
            sentiment=sentiment,
            priority=priority,
            risk_level=risk_level,
            agreements=agreements,
            risks=risks,
            missing_info=missing_info,
            next_steps=next_steps,
            follow_up=FollowUp(
                needed=True,
                date=next_steps[0].due_date,
                reason="Follow-up extracted from the communication context.",
            ),
            recommended_tasks=recommended_tasks,
            timeline_comment="",
            draft_reply=(
                "Draft only: thank the client, restate the request, confirm the next contact step, "
                "and avoid claiming any action was already executed."
            ),
            confidence=confidence,
            review_reason=review_reason,
            human_approval_required=human_approval_required,
            model_used="mock-ai-provider",
        )
        result.timeline_comment = format_timeline_comment(result)
        return result
