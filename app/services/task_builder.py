from __future__ import annotations

from datetime import date, timedelta

from app.schemas import RecommendedTask, SummaryResult


def build_consolidated_task(summary: SummaryResult, responsible_id: int | None) -> RecommendedTask:
    due_date = date.today() + timedelta(days=2)
    if summary.recommended_tasks:
        first = summary.recommended_tasks[0]
        due_date = first.due_date or due_date
    description = "\n".join(
        [
            f"Summary: {summary.summary}",
            f"Intent: {summary.client_intent}",
            f"Risks: {', '.join(summary.risks) or 'none'}",
            f"Missing info: {', '.join(summary.missing_info) or 'none'}",
        ]
    )
    return RecommendedTask(
        title=f"Follow up: {summary.client_intent[:60]}",
        description=description,
        priority=summary.priority,
        due_date=due_date,
        responsible_id=responsible_id,
    )
