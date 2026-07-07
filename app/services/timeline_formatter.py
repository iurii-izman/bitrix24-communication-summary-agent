from __future__ import annotations

from app.schemas import SummaryResult


def format_timeline_comment(summary: SummaryResult) -> str:
    agreements = "\n".join(f"- {item}" for item in summary.agreements) or "- None"
    risks = "\n".join(f"- {item}" for item in summary.risks) or "- None"
    missing_info = "\n".join(f"- {item}" for item in summary.missing_info) or "- None"
    next_steps = (
        "\n".join(f"- {step.title} ({step.owner})" for step in summary.next_steps) or "- None"
    )
    follow_up = (
        f"{summary.follow_up.reason}"
        if not summary.follow_up.date
        else f"{summary.follow_up.date.isoformat()} - {summary.follow_up.reason}"
    )
    return (
        "🤖 Communication Summary Agent\n\n"
        f"Краткое summary:\n{summary.summary}\n\n"
        f"Намерение клиента:\n{summary.client_intent}\n\n"
        f"Договорённости:\n{agreements}\n\n"
        f"Риски:\n{risks}\n\n"
        f"Недостающая информация:\n{missing_info}\n\n"
        f"Следующие шаги:\n{next_steps}\n\n"
        f"Follow-up:\n{follow_up}\n\n"
        f"Черновик ответа:\n{summary.draft_reply}\n\n"
        f"Human approval required: {str(summary.human_approval_required).lower()}\n"
        f"Model: {summary.model_used}"
    )
