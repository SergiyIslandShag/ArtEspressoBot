from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from bot.config import Settings


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, settings: Settings) -> bool:
        return event.from_user.id in settings.admin_telegram_ids

