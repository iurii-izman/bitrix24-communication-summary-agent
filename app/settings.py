from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bitrix24 Communication Summary Agent"
    app_mode: str = "demo"
    database_url: str = "sqlite+pysqlite:///./demo.sqlite3"
    webhook_secret: str = "dev-webhook-secret"
    admin_username: str = "admin"
    admin_password: str = "admin"
    ai_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    bitrix_mode: str = "mock"
    bitrix_crm_mode: str = "legacy"
    bitrix_webhook_url: str = ""
    bitrix_responsible_id: int = 1
    allow_bitrix_write: bool = False
    masking_enabled: bool = True
    worker_auto_run: bool = True
    review_confidence_threshold: float = 0.70
    rate_limit_window_seconds: int = 60
    rate_limit_max_requests: int = 30
    provider_timeout_seconds: float = 20.0
    bitrix_timeout_seconds: float = 10.0
    max_retry_count: int = 2
    short_text_drop_threshold: int = 6
    app_debug: bool = False
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def has_openai_credentials(self) -> bool:
        return bool(self.openai_api_key.strip())

    @property
    def masked_database_url(self) -> str:
        value = self.database_url
        if "///" in value:
            prefix, tail = value.split("///", 1)
            filename = tail.rsplit("/", 1)[-1]
            return f"{prefix}///.../{filename}"
        return "***"

    @property
    def safe_settings_snapshot(self) -> dict[str, object]:
        return {
            "app_name": self.app_name,
            "app_mode": self.app_mode,
            "database_url": self.masked_database_url,
            "ai_provider": self.ai_provider,
            "bitrix_mode": self.bitrix_mode,
            "bitrix_crm_mode": self.bitrix_crm_mode,
            "allow_bitrix_write": "enabled" if self.allow_bitrix_write else "disabled",
            "masking_enabled": "enabled" if self.masking_enabled else "disabled",
            "worker_auto_run": "enabled" if self.worker_auto_run else "disabled",
            "review_confidence_threshold": self.review_confidence_threshold,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
