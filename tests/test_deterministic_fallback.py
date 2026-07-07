from app.schemas import CommunicationCreate
from app.services.deterministic_fallback import DeterministicFallback


def test_fallback_returns_valid_summary_result() -> None:
    result = DeterministicFallback().summarize(
        CommunicationCreate(
            idempotency_key="xxx",
            source="manual",
            channel="email",
            communication_text="Need CRM help.",
        )
    )
    assert result.model_used == "deterministic-fallback"
    assert result.summary
    assert result.human_approval_required is True
