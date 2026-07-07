from __future__ import annotations

import re

EMAIL_RE = re.compile(r"\b([A-Za-z0-9._%+-])([A-Za-z0-9._%+-]*)(@[\w.-]+\.\w+)\b")
PHONE_RE = re.compile(r"(\+?\d{3})(\d{2,6})(\d{4})")
BITRIX_WEBHOOK_RE = re.compile(r"https?://[^\s]+/rest/\d+/[A-Za-z0-9_/-]+/?")
SECRET_RE = re.compile(
    r"(?i)\b(access_token|refresh_token|application_token|secret|openai_api_key)\b\s*[:=]\s*([^\s,;]+)"
)


def mask_email(value: str) -> str:
    return EMAIL_RE.sub(lambda match: f"{match.group(1)}***{match.group(3)}", value)


def mask_phone(value: str) -> str:
    return PHONE_RE.sub(lambda match: f"{match.group(1)}***{match.group(3)}", value)


def mask_webhook_url(value: str) -> str:
    return BITRIX_WEBHOOK_RE.sub("***BITRIX_WEBHOOK_URL***", value)


def mask_secrets(value: str) -> str:
    return SECRET_RE.sub(lambda match: f"{match.group(1)}=***", value)


def sanitize_error(value: str) -> str:
    return mask_text(value)


def mask_text(value: str | None) -> str | None:
    if value is None:
        return None
    masked = mask_email(value)
    masked = mask_phone(masked)
    masked = mask_webhook_url(masked)
    masked = mask_secrets(masked)
    return masked
