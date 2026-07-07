from app.masking import mask_email, mask_phone, mask_secrets, mask_webhook_url, sanitize_error


def test_masks_email() -> None:
    assert mask_email("john@example.com") == "j***@example.com"


def test_masks_phone() -> None:
    assert mask_phone("+37312345678") == "+373***5678"


def test_masks_secret() -> None:
    assert "secret=***" in mask_secrets("secret=abcdef")


def test_masks_webhook_url() -> None:
    assert (
        mask_webhook_url("https://domain.bitrix24.ru/rest/1/abc123/")
        == "***BITRIX_WEBHOOK_URL***"
    )


def test_errors_sanitized() -> None:
    assert "***" in sanitize_error("secret=abcdef and john@example.com")
