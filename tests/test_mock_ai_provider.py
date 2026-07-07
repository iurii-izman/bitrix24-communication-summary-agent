from app.schemas import CommunicationCreate
from app.services.mock_ai_provider import MockCommunicationAIProvider


def test_high_value_text_returns_meaningful_summary() -> None:
    provider = MockCommunicationAIProvider(0.7)
    result = provider.summarize(
        CommunicationCreate(
            idempotency_key="aaa",
            source="manual",
            channel="call_transcript",
            communication_text=(
                "Client wants Bitrix24 and 1C integration, "
                "asked for proposal and callback Friday."
            ),
        )
    )
    assert result.priority in {"medium", "high"}
    assert "proposal" in result.summary.lower() or result.agreements
    assert result.follow_up.needed is True


def test_vague_text_returns_low_confidence_review() -> None:
    provider = MockCommunicationAIProvider(0.7)
    result = provider.summarize(
        CommunicationCreate(
            idempotency_key="bbb",
            source="manual",
            channel="chat",
            communication_text="call me later",
        )
    )
    assert result.confidence < 0.7
    assert result.human_approval_required is True
