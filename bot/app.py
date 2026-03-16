from __future__ import annotations

from aiogram import Dispatcher

from bot.config import Settings
from bot.handlers import admin, ingredients, menu, service, start
from bot.middlewares.db import DbSessionMiddleware
from bot.db.session import make_engine, make_session_factory


def build_dispatcher(settings: Settings) -> Dispatcher:
    dp = Dispatcher()

    engine = make_engine(settings.database_url)
    session_factory = make_session_factory(engine)
    dp.update.middleware(DbSessionMiddleware(session_factory=session_factory, settings=settings))

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(ingredients.router)
    dp.include_router(service.router)
    dp.include_router(menu.router)

    return dp

