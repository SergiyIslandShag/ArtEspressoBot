from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.common import main_menu_kb
from bot.states import IngredientsOrderSG, ServiceOrderSG


router = Router(name=__name__)


@router.callback_query(lambda c: c.data == "menu:home")
async def menu_home(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Головне меню:", reply_markup=main_menu_kb())
    await callback.answer()


@router.message()
async def fallback_text(message: Message, state: FSMContext) -> None:
    # If user types random text outside flows, show menu.
    if await state.get_state() in (IngredientsOrderSG.comment.state, ServiceOrderSG.comment.state):
        return
    await message.answer("Головне меню:", reply_markup=main_menu_kb())

