from base64 import b64encode


def _admin_headers() -> dict[str, str]:
    token = b64encode(b"admin:admin").decode("utf-8")
    return {"Authorization": f"Basic {token}"}


def _create(client, auth_headers, key: str, text: str) -> str:
    response = client.post(
        "/api/v1/communications",
        headers=auth_headers,
        json={
            "idempotency_key": key,
            "source": "manual",
            "channel": "chat",
            "communication_text": text,
        },
    )
    return response.json()["request_id"]


def test_approve_works(client, auth_headers) -> None:
    request_id = _create(client, auth_headers, "adm-1", "call me later")
    response = client.post(
        f"/admin/communications/{request_id}/approve",
        headers=_admin_headers(),
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_retry_works(client, auth_headers) -> None:
    request_id = _create(client, auth_headers, "adm-2", "call me later")
    response = client.post(
        f"/admin/communications/{request_id}/retry",
        headers=_admin_headers(),
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_drop_works(client, auth_headers) -> None:
    request_id = _create(client, auth_headers, "adm-3", "call me later")
    response = client.post(
        f"/admin/communications/{request_id}/drop",
        headers=_admin_headers(),
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_reprocess_ai_works(client, auth_headers) -> None:
    request_id = _create(
        client,
        auth_headers,
        "adm-4",
        "Client asked for Bitrix24 proposal and callback Friday.",
    )
    response = client.post(
        f"/admin/communications/{request_id}/reprocess-ai",
        headers=_admin_headers(),
        follow_redirects=False,
    )
    assert response.status_code == 303
