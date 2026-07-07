from __future__ import annotations

from datetime import date as dt_date
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Channel(StrEnum):
    call_transcript = "call_transcript"
    email = "email"
    chat = "chat"
    manager_note = "manager_note"
    meeting_note = "meeting_note"
    crm_comment = "crm_comment"
    other = "other"


class CommunicationStatus(StrEnum):
    received = "received"
    processing = "processing"
    summarized = "summarized"
    review_needed = "review_needed"
    approved = "approved"
    bitrix_syncing = "bitrix_syncing"
    completed = "completed"
    duplicate = "duplicate"
    dropped = "dropped"
    failed_retryable = "failed_retryable"
    failed = "failed"


class PriorityLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class RiskLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class Sentiment(StrEnum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"
    mixed = "mixed"
    unknown = "unknown"


class NextStep(BaseModel):
    title: str
    owner: str
    due_date: dt_date | None = None
    rationale: str


class FollowUp(BaseModel):
    needed: bool
    date: dt_date | None = None
    reason: str


class RecommendedTask(BaseModel):
    title: str
    description: str
    priority: PriorityLevel
    due_date: dt_date | None = None
    responsible_id: int | None = None


class SummaryResult(BaseModel):
    summary: str
    client_intent: str
    sentiment: Sentiment = Sentiment.unknown
    priority: PriorityLevel = PriorityLevel.medium
    risk_level: RiskLevel = RiskLevel.medium
    agreements: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    next_steps: list[NextStep] = Field(default_factory=list)
    follow_up: FollowUp
    recommended_tasks: list[RecommendedTask] = Field(default_factory=list)
    timeline_comment: str
    draft_reply: str
    confidence: float = Field(ge=0.0, le=1.0)
    review_reason: str | None = None
    human_approval_required: bool = True
    model_used: str


class CommunicationCreate(BaseModel):
    idempotency_key: str = Field(min_length=3, max_length=120)
    source: str = Field(min_length=2, max_length=50)
    channel: Channel
    external_deal_id: str | None = None
    external_lead_id: str | None = None
    client_name: str | None = None
    client_contact: str | None = None
    communication_text: str = Field(min_length=1, max_length=20000)
    current_stage: str | None = None
    manager_notes: str | None = None

    @field_validator("communication_text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("communication_text must not be empty")
        return stripped


class CommunicationSubmitResponse(BaseModel):
    ok: bool = True
    request_id: str
    status: CommunicationStatus
    message: str | None = None


class ProcessingLogEntry(BaseModel):
    event_type: str
    from_status: str | None = None
    to_status: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class CommunicationDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: str
    idempotency_key: str
    source: str
    channel: Channel
    external_deal_id: str | None = None
    external_lead_id: str | None = None
    client_name: str | None = None
    client_contact: str | None = None
    communication_text: str
    current_stage: str | None = None
    manager_notes: str | None = None
    status: CommunicationStatus
    priority: PriorityLevel | None = None
    risk_level: RiskLevel | None = None
    retry_count: int
    last_error: str | None = None
    summary_result: SummaryResult | None = None
    masked_payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    logs: list[ProcessingLogEntry] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    app_name: str
    app_mode: str
    ai_provider: str
    bitrix_mode: str
    allow_bitrix_write: bool
    db_ok: bool


class RoutingDecision(BaseModel):
    decision: str
    reason: str
    required_human_review: bool
