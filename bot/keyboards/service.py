from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


SERVICE_TYPES: list[tuple[str, str]] = [
    ("maintenance", "Планове ТО"),
    ("diagnostics", "Діагностика"),
    ("repair", "Ремонт"),
    ("setup", "Налаштування"),
    ("other", "Інше"),
]


def service_types_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, title in SERVICE_TYPES:
        kb.button(text=title, callback_data=f"svc:type:{code}")
    kb.button(text="⬅️ Меню", callback_data="menu:home")
    kb.adjust(1)
    return kb.as_markup()


def service_media_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Готово", callback_data="svc:media:done")
    kb.button(text="⬅️ Меню", callback_data="menu:home")
    kb.adjust(1)
    return kb.as_markup()


def service_submit_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Відправити", callback_data="svc:submit:yes")
    kb.button(text="❌ Скасувати", callback_data="svc:submit:no")
    kb.adjust(1)
    return kb.as_markup()

