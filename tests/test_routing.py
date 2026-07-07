from app.schemas import (
    Channel,
    CommunicationCreate,
    FollowUp,
    NextStep,
    PriorityLevel,
    RiskLevel,
    SummaryResult,
)
from app.services.routing import RoutingService


def _summary(confidence: float, risk: str, missing_info=None) -> SummaryResult:
    return SummaryResult(
        summary="s",
        client_intent="i",
        sentiment="neutral",
        priority=PriorityLevel.medium,
        risk_level=risk,
        agreements=[],
        risks=[],
        missing_info=missing_info or [],
        next_steps=[NextStep(title="x", owner="y", rationale="z")],
        follow_up=FollowUp(needed=True, reason="r"),
        recommended_tasks=[],
        timeline_comment="x",
        draft_reply="y",
        confidence=confidence,
        human_approval_required=False,
        model_used="mock",
    )


def _payload(text: str) -> CommunicationCreate:
    return CommunicationCreate(
        idempotency_key="route-1",
        source="manual",
        channel=Channel.email,
        communication_text=text,
    )


def test_low_confidence_goes_to_review(settings) -> None:
    decision = RoutingService(settings).decide(
        _payload("Client asked for CRM scope clarification in detail"),
        _summary(0.4, "low"),
    )
    assert decision.decision == "review_needed"


def test_high_risk_goes_to_review(settings) -> None:
    decision = RoutingService(settings).decide(
        _payload("Client is unhappy and urgent"),
        _summary(0.9, RiskLevel.high),
    )
    assert decision.decision == "review_needed"


def test_normal_case_proceeds(settings) -> None:
    decision = RoutingService(settings).decide(
        _payload("Client needs a full Bitrix24 implementation scope discussion tomorrow"),
        _summary(0.9, "low", []),
    )
    assert decision.decision == "proceed"
