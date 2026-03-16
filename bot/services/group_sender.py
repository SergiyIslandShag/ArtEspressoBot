from __future__ import annotations

from typing import Any

from aiogram import Bot
from aiogram.types import InputMediaPhoto, InputMediaVideo

from bot.config import Settings
from bot.db.models import Client, Order, OrderType, PriceTier


def _tier_label(client: Client) -> str:
    tier = client.price_tier.value if isinstance(client.price_tier, PriceTier) else str(client.price_tier)
    regular = "Regular" if client.is_regular else "Standard"
    return f"{regular} / {tier}"


def format_order_summary(client: Client, order: Order) -> str:
    header = [
        "🧾 Нова заявка",
        f"Клієнт: {client.name or '-'}",
        f"Телефон: {client.phone or '-'}",
        f"Telegram ID: {client.telegram_id}",
        f"Статус цін: {_tier_label(client)}",
        "",
    ]

    if order.type == OrderType.ingredients:
        payload: dict[str, Any] = dict(order.payload or {})
        items: list[dict[str, Any]] = list(payload.get("items") or [])
        lines = ["Тип: Інгредієнти"]
        for i, row in enumerate(items, start=1):
            title = row.get("title") or row.get("item")
            qty = row.get("qty")
            lines.append(f"{i}. {title}: {qty}")
        comment = payload.get("comment")
        if comment:
            lines.append("")
            lines.append(f"Коментар: {comment}")
        return "\n".join(header + lines)

    payload = dict(order.payload or {})
    lines = [
        "Тип: Сервіс",
        f"Варіант: {payload.get('service_type_title') or payload.get('service_type') or '-'}",
        f"Модель: {payload.get('machine_model') or '-'}",
    ]
    comment = payload.get("comment")
    if comment:
        lines.append(f"Коментар: {comment}")
    return "\n".join(header + lines)


async def send_order_to_group(bot: Bot, settings: Settings, *, client: Client, order: Order) -> None:
    text = format_order_summary(client, order)

    if order.type != OrderType.service or not order.media:
        await bot.send_message(chat_id=settings.group_chat_id, text=text)
        return

    media_group = []
    for m in order.media:
        mtype = m.get("type")
        file_id = m.get("file_id")
        if not file_id:
            continue
        if mtype == "photo":
            media_group.append(InputMediaPhoto(media=file_id))
        elif mtype == "video":
            media_group.append(InputMediaVideo(media=file_id))

    if media_group:
        await bot.send_media_group(chat_id=settings.group_chat_id, media=media_group)
    await bot.send_message(chat_id=settings.group_chat_id, text=text)

