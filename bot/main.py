from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.app import build_dispatcher
from bot.config import load_settings
from bot.logging_utils import setup_logging


async def main() -> None:
    setup_logging()
    settings = load_settings()

    bot = Bot(token=settings.bot_token)
    dp: Dispatcher = build_dispatcher(settings)

    # Polling cannot work while a webhook is active for this token.
    await bot.delete_webhook(drop_pending_updates=True)
    logging.getLogger(__name__).info("Bot starting polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

