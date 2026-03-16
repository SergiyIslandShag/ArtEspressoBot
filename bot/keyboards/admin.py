from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Клієнти: знайти", callback_data="admin:clients:search")
    kb.button(text="⬅️ Меню", callback_data="menu:home")
    kb.adjust(1)
    return kb.as_markup()


def admin_client_actions_kb(client_id: int, *, is_regular: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=("Зробити Standard" if is_regular else "Зробити Regular"),
        callback_data=f"admin:client:{client_id}:toggle_regular",
    )
    kb.button(text="Ціни: standard", callback_data=f"admin:client:{client_id}:tier:standard")
    kb.button(text="Ціни: regular", callback_data=f"admin:client:{client_id}:tier:regular")
    kb.button(text="⬅️ Адмін-меню", callback_data="admin:home")
    kb.adjust(1)
    return kb.as_markup()

