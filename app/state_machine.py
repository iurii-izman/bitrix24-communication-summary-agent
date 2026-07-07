from app.schemas import CommunicationStatus

ALLOWED_TRANSITIONS: dict[CommunicationStatus, set[CommunicationStatus]] = {
    CommunicationStatus.received: {
        CommunicationStatus.processing,
        CommunicationStatus.duplicate,
        CommunicationStatus.dropped,
    },
    CommunicationStatus.processing: {
        CommunicationStatus.summarized,
        CommunicationStatus.failed_retryable,
        CommunicationStatus.failed,
    },
    CommunicationStatus.summarized: {
        CommunicationStatus.review_needed,
        CommunicationStatus.bitrix_syncing,
    },
    CommunicationStatus.review_needed: {
        CommunicationStatus.approved,
        CommunicationStatus.dropped,
    },
    CommunicationStatus.approved: {CommunicationStatus.bitrix_syncing},
    CommunicationStatus.bitrix_syncing: {
        CommunicationStatus.completed,
        CommunicationStatus.failed_retryable,
    },
    CommunicationStatus.failed_retryable: {
        CommunicationStatus.processing,
        CommunicationStatus.failed,
    },
    CommunicationStatus.failed: {CommunicationStatus.dropped},
    CommunicationStatus.completed: set(),
    CommunicationStatus.duplicate: set(),
    CommunicationStatus.dropped: set(),
}


def validate_transition(from_status: CommunicationStatus, to_status: CommunicationStatus) -> None:
    if to_status not in ALLOWED_TRANSITIONS[from_status]:
        raise ValueError(f"Invalid transition: {from_status.value} -> {to_status.value}")
