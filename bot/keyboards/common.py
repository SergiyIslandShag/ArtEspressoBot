from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Старт", callback_data="start:go")
    return kb.as_markup()


def main_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Замовити інгредієнти", callback_data="menu:ingredients")
    kb.button(text="Замовити сервіс", callback_data="menu:service")
    kb.adjust(1)
    return kb.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Меню", callback_data="menu:home")
    return kb.as_markup()


def skip_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Пропустити", callback_data="flow:skip")
    return kb.as_markup()

