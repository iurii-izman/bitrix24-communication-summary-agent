from __future__ import annotations

import json

import httpx
from pydantic import ValidationError

from app.schemas import CommunicationCreate, SummaryResult
from app.services.ai_provider import CommunicationAIProvider
from app.services.deterministic_fallback import DeterministicFallback
from app.services.timeline_formatter import format_timeline_comment
from app.settings import Settings


class OpenAICommunicationProvider(CommunicationAIProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.fallback = DeterministicFallback()

    def summarize(self, payload: CommunicationCreate) -> SummaryResult:
        if not self.settings.has_openai_credentials:
            return self.fallback.summarize(payload)
        prompt = {
            "instructions": [
                "Return JSON only.",
                "Do not claim any action was executed.",
                "Do not send a client message.",
                "Keep human-in-the-loop.",
                "Draft reply is only a draft.",
            ],
            "communication": payload.model_dump(mode="json"),
        }
        try:
            with httpx.Client(timeout=self.settings.provider_timeout_seconds) as client:
                response = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                    json={
                        "model": self.settings.openai_model,
                        "response_format": {"type": "json_object"},
                        "messages": [
                            {
                                "role": "user",
                                "content": json.dumps(prompt, ensure_ascii=False),
                            }
                        ],
                    },
                )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
            result = SummaryResult.model_validate_json(content)
            result.timeline_comment = format_timeline_comment(result)
            return result
        except (httpx.HTTPError, KeyError, ValidationError, json.JSONDecodeError):
            return self.fallback.summarize(payload)
