import pytest

from app.schemas import CommunicationStatus
from app.state_machine import validate_transition


def test_valid_transitions_allowed() -> None:
    validate_transition(CommunicationStatus.received, CommunicationStatus.processing)
    validate_transition(CommunicationStatus.processing, CommunicationStatus.summarized)
    validate_transition(CommunicationStatus.summarized, CommunicationStatus.review_needed)
    validate_transition(CommunicationStatus.review_needed, CommunicationStatus.approved)
    validate_transition(CommunicationStatus.approved, CommunicationStatus.bitrix_syncing)


def test_invalid_transition_rejected() -> None:
    with pytest.raises(ValueError):
        validate_transition(CommunicationStatus.received, CommunicationStatus.completed)
