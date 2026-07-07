from scripts._bitrix_validation_common import build_artifact_record, extract_bitrix_refs


def test_extract_bitrix_refs_reads_ids() -> None:
    detail = {
        "request_id": "abc",
        "status": "completed",
        "external_deal_id": "1",
        "priority": "high",
        "risk_level": "medium",
        "logs": [
            {
                "event_type": "bitrix_actions_planned",
                "metadata": {
                    "timeline": {"result": {"result": 133}},
                    "task": {"result": {"result": {"task": {"id": "19"}}}},
                },
            }
        ],
    }
    refs = extract_bitrix_refs(detail)
    assert refs["timeline_comment_id"] == 133
    assert refs["task_id"] == 19


def test_build_artifact_record_handles_review_case() -> None:
    detail = {
        "request_id": "def",
        "status": "review_needed",
        "external_deal_id": "1",
        "priority": "low",
        "risk_level": "low",
        "logs": [],
    }
    record = build_artifact_record(
        scenario="review",
        detail=detail,
        write_enabled=True,
    )
    assert record["timeline_comment_id"] is None
    assert record["task_id"] is None
