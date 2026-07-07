import pytest
from pydantic import ValidationError

from app.schemas import CommunicationCreate


def test_valid_payload_accepted() -> None:
    payload = CommunicationCreate(
        idempotency_key="demo-1",
        source="manual",
        channel="call_transcript",
        communication_text="Client asked for Bitrix24 proposal.",
    )
    assert payload.channel == "call_transcript"


def test_invalid_channel_rejected() -> None:
    with pytest.raises(ValidationError):
        CommunicationCreate(
            idempotency_key="demo-1",
            source="manual",
            channel="bad-channel",
            communication_text="Text",
        )


def test_empty_communication_text_rejected() -> None:
    with pytest.raises(ValidationError):
        CommunicationCreate(
            idempotency_key="demo-1",
            source="manual",
            channel="email",
            communication_text="   ",
        )
