from __future__ import annotations

from typing import FrozenSet

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bot_token: str = Field(alias="BOT_TOKEN")
    database_url: str = Field(alias="DATABASE_URL")
    group_chat_id: int = Field(alias="GROUP_CHAT_ID")

    admin_telegram_ids_raw: str = Field(default="", alias="ADMIN_TELEGRAM_IDS")
    require_existing_client: bool = Field(default=False, alias="REQUIRE_EXISTING_CLIENT")

    @property
    def admin_telegram_ids(self) -> FrozenSet[int]:
        raw = (self.admin_telegram_ids_raw or "").strip()
        if not raw:
            return frozenset()
        ids: list[int] = []
        for part in raw.split(","):
            part = part.strip()
            if part:
                ids.append(int(part))
        return frozenset(ids)


def load_settings() -> Settings:
    return Settings()
