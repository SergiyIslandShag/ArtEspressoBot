from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


INGREDIENT_ITEMS: list[tuple[str, str]] = [
    ("coffee", "Кава"),
    ("milk_powder", "Сухе молоко"),
    ("sugar", "Цукор"),
    ("syrups", "Сиропи"),
    ("cups", "Стакани"),
    ("cleaning_liquid", "Очисна рідина"),
    ("tablets", "Таблетки"),
]


def ingredients_items_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, title in INGREDIENT_ITEMS:
        kb.button(text=title, callback_data=f"ing:item:{code}")
    kb.button(text="✅ Підтвердити", callback_data="ing:confirm")
    kb.button(text="⬅️ Меню", callback_data="menu:home")
    kb.adjust(1)
    return kb.as_markup()


def ingredients_after_qty_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Додати ще", callback_data="ing:more")
    kb.button(text="✅ Підтвердити", callback_data="ing:confirm")
    kb.button(text="⬅️ Меню", callback_data="menu:home")
    kb.adjust(1)
    return kb.as_markup()


def ingredients_submit_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Відправити", callback_data="ing:submit:yes")
    kb.button(text="❌ Скасувати", callback_data="ing:submit:no")
    kb.adjust(1)
    return kb.as_markup()

