def _payload() -> dict[str, object]:
    return {
        "idempotency_key": "call-0001",
        "source": "manual",
        "channel": "call_transcript",
        "external_deal_id": "123",
        "client_name": "Demo Client",
        "client_contact": "+37300000000",
        "communication_text": (
            "Client asked for Bitrix24 implementation "
            "with 1C integration and proposal."
        ),
        "current_stage": "qualification",
        "manager_notes": "Need quick follow-up.",
    }


def test_requires_webhook_secret(client) -> None:
    response = client.post("/api/v1/communications", json=_payload())
    assert response.status_code == 401


def test_valid_request_creates_record(client, auth_headers) -> None:
    response = client.post("/api/v1/communications", headers=auth_headers, json=_payload())
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["request_id"]


def test_lookup_works(client, auth_headers) -> None:
    created = client.post("/api/v1/communications", headers=auth_headers, json=_payload())
    request_id = created.json()["request_id"]
    detail = client.get(f"/api/v1/communications/{request_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["request_id"] == request_id
