from scripts._bitrix_validation_common import build_artifact_record


def test_artifact_record_preserves_external_deal_id() -> None:
    detail = {
        "request_id": "xyz",
        "status": "completed",
        "external_deal_id": "42",
        "priority": "medium",
        "risk_level": "low",
        "logs": [],
    }
    record = build_artifact_record(
        scenario="case",
        detail=detail,
        write_enabled=False,
    )
    assert record["external_deal_id"] == "42"
