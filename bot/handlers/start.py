from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import Settings
from bot.keyboards.common import main_menu_kb, start_kb
from bot.services.db_ops import get_client_by_telegram_id, get_or_create_client, update_client_profile
from bot.states import RegistrationSG


router = Router(name=__name__)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Вітаю! Це бот ArtEspresso.\n\nНатисніть «Старт», щоб продовжити.",
        reply_markup=start_kb(),
    )


@router.callback_query(lambda c: c.data == "start:go")
async def start_go(callback: CallbackQuery, session: AsyncSession, settings: Settings, state: FSMContext) -> None:
    telegram_id = callback.from_user.id
    client = await get_client_by_telegram_id(session, telegram_id)

    if settings.require_existing_client and client is None:
        await callback.message.answer("Доступ обмежено. Будь ласка, зв’яжіться з менеджером.")
        await callback.answer()
        return

    client = await get_or_create_client(session, telegram_id)

    if not client.phone:
        await state.set_state(RegistrationSG.name)
        await callback.message.answer("Як до вас звертатися? (ПІБ/назва)")
    else:
        await callback.message.answer("Головне меню:", reply_markup=main_menu_kb())

    await callback.answer()


@router.message(RegistrationSG.name)
async def reg_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("Будь ласка, введіть ім’я/назву текстом.")
        return
    await state.update_data(name=name)
    await state.set_state(RegistrationSG.phone)
    await message.answer("Введіть номер телефону (можна у форматі +380...).")


@router.message(RegistrationSG.phone)
async def reg_phone(message: Message, session: AsyncSession, state: FSMContext) -> None:
    phone = None
    if message.contact and message.contact.phone_number:
        phone = message.contact.phone_number
    else:
        phone = (message.text or "").strip()

    if not phone:
        await message.answer("Будь ласка, введіть телефон текстом або надішліть контакт.")
        return

    data = await state.get_data()
    name = data.get("name")
    await update_client_profile(session, message.from_user.id, name=name, phone=phone)
    await state.clear()
    await message.answer("Дякую! Дані збережено.\n\nГоловне меню:", reply_markup=main_menu_kb())

