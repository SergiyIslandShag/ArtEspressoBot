from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Client, PriceTier
from bot.filters.admin import IsAdmin
from bot.keyboards.admin import admin_client_actions_kb, admin_menu_kb
from bot.services.db_ops import admin_search_clients, admin_set_client_price_tier
from bot.states import AdminSG


router = Router(name=__name__)
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(Command("admin"))
async def admin_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminSG.choosing_action)
    await message.answer("Адмін-меню:", reply_markup=admin_menu_kb())


@router.callback_query(lambda c: c.data == "admin:home")
async def admin_home(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminSG.choosing_action)
    await callback.message.answer("Адмін-меню:", reply_markup=admin_menu_kb())
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin:clients:search")
async def admin_search_begin(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminSG.searching)
    await callback.message.answer("Введіть телефон / ім’я / Telegram ID клієнта для пошуку.")
    await callback.answer()


@router.message(AdminSG.searching)
async def admin_search_do(message: Message, session: AsyncSession, state: FSMContext) -> None:
    query = (message.text or "").strip()
    results = await admin_search_clients(session, query)
    if not results:
        await message.answer("Нічого не знайдено. Спробуйте інший запит або /admin.")
        return

    # Show the most recent match first
    client = results[0]
    await state.update_data(last_client_id=client.id)
    await state.set_state(AdminSG.choosing_action)

    text = (
        "Клієнт знайдений:\n"
        f"ID: {client.id}\n"
        f"Name: {client.name or '-'}\n"
        f"Phone: {client.phone or '-'}\n"
        f"Telegram ID: {client.telegram_id}\n"
        f"is_regular: {client.is_regular}\n"
        f"price_tier: {client.price_tier.value}\n"
    )
    await message.answer(text, reply_markup=admin_client_actions_kb(client.id, is_regular=client.is_regular))


@router.callback_query(lambda c: c.data and c.data.startswith("admin:client:") and ":toggle_regular" in c.data)
async def admin_toggle_regular(callback: CallbackQuery, session: AsyncSession) -> None:
    # admin:client:{id}:toggle_regular
    parts = callback.data.split(":")
    client_id = int(parts[2])
    q = await session.execute(select(Client).where(Client.id == client_id))
    client = q.scalar_one_or_none()
    if not client:
        await callback.message.answer("Клієнта не знайдено.")
        await callback.answer()
        return
    client.is_regular = not client.is_regular
    await session.commit()

    await callback.message.answer(
        f"Оновлено: is_regular={client.is_regular}",
        reply_markup=admin_client_actions_kb(client_id, is_regular=client.is_regular),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("admin:client:") and ":tier:" in c.data)
async def admin_set_tier(callback: CallbackQuery, session: AsyncSession) -> None:
    # admin:client:{id}:tier:{tier}
    parts = callback.data.split(":")
    client_id = int(parts[2])
    tier_str = parts[4]
    tier = PriceTier(tier_str)
    client = await admin_set_client_price_tier(session, client_id, tier)
    if not client:
        await callback.message.answer("Клієнта не знайдено.")
        await callback.answer()
        return

    await callback.message.answer(
        f"Оновлено: price_tier={client.price_tier.value}",
        reply_markup=admin_client_actions_kb(client_id, is_regular=client.is_regular),
    )
    await callback.answer()

