from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import Settings
from bot.keyboards.common import skip_kb
from bot.keyboards.ingredients import (
    INGREDIENT_ITEMS,
    ingredients_after_qty_kb,
    ingredients_items_kb,
    ingredients_submit_kb,
)
from bot.services.db_ops import create_order, get_or_create_client
from bot.services.db_ops import mark_order_sent
from bot.services.group_sender import send_order_to_group
from bot.states import IngredientsOrderSG
from bot.db.models import OrderType


router = Router(name=__name__)


def _title_for_item(code: str) -> str:
    for c, t in INGREDIENT_ITEMS:
        if c == code:
            return t
    return code


@router.callback_query(lambda c: c.data == "menu:ingredients")
async def ingredients_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(IngredientsOrderSG.choosing_item)
    await state.update_data(cart=[])
    await callback.message.answer("Оберіть інгредієнт зі списку та вкажіть кількість.", reply_markup=ingredients_items_kb())
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("ing:item:"))
async def ingredients_choose_item(callback: CallbackQuery, state: FSMContext) -> None:
    code = callback.data.split(":", 2)[2]
    await state.update_data(selected_item=code)
    await state.set_state(IngredientsOrderSG.entering_qty)
    await callback.message.answer(f"Введіть кількість для «{_title_for_item(code)}» (число).")
    await callback.answer()


@router.message(IngredientsOrderSG.entering_qty)
async def ingredients_qty(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip().replace(",", ".")
    try:
        qty = float(raw)
    except ValueError:
        await message.answer("Введіть кількість числом, наприклад: 2 або 0.5")
        return
    if qty <= 0:
        await message.answer("Кількість має бути більшою за 0.")
        return

    data = await state.get_data()
    code = data.get("selected_item")
    if not code:
        await state.set_state(IngredientsOrderSG.choosing_item)
        await message.answer("Оберіть інгредієнт.", reply_markup=ingredients_items_kb())
        return

    cart: list[dict] = list(data.get("cart") or [])
    cart.append({"item": code, "title": _title_for_item(code), "qty": qty})
    await state.update_data(cart=cart, selected_item=None)
    await state.set_state(IngredientsOrderSG.choosing_item)
    await message.answer("Додано. Можна додати ще або підтвердити.", reply_markup=ingredients_after_qty_kb())


@router.callback_query(lambda c: c.data == "ing:more")
async def ingredients_more(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(IngredientsOrderSG.choosing_item)
    await callback.message.answer("Оберіть наступний інгредієнт.", reply_markup=ingredients_items_kb())
    await callback.answer()


@router.callback_query(lambda c: c.data == "ing:confirm")
async def ingredients_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    cart: list[dict] = list(data.get("cart") or [])
    if not cart:
        await callback.message.answer("Кошик порожній. Оберіть хоча б один інгредієнт.", reply_markup=ingredients_items_kb())
        await callback.answer()
        return
    await state.set_state(IngredientsOrderSG.comment)
    await callback.message.answer("Додайте коментар до замовлення (опційно).", reply_markup=skip_kb())
    await callback.answer()


@router.callback_query(lambda c: c.data == "flow:skip")
async def ingredients_skip_comment(callback: CallbackQuery, state: FSMContext) -> None:
    if await state.get_state() != IngredientsOrderSG.comment.state:
        await callback.answer()
        return
    await state.update_data(comment=None)
    await state.set_state(IngredientsOrderSG.confirm)
    await _send_ingredients_summary(callback.message, state)
    await callback.answer()


@router.message(IngredientsOrderSG.comment)
async def ingredients_comment(message: Message, state: FSMContext) -> None:
    comment = (message.text or "").strip()
    await state.update_data(comment=comment or None)
    await state.set_state(IngredientsOrderSG.confirm)
    await _send_ingredients_summary(message, state)


async def _send_ingredients_summary(target: Message, state: FSMContext) -> None:
    data = await state.get_data()
    cart: list[dict] = list(data.get("cart") or [])
    comment = data.get("comment")

    lines = ["Ваше замовлення (інгредієнти):"]
    for i, row in enumerate(cart, start=1):
        lines.append(f"{i}. {row['title']}: {row['qty']}")
    if comment:
        lines.append("")
        lines.append(f"Коментар: {comment}")

    await target.answer("\n".join(lines), reply_markup=ingredients_submit_kb())


@router.callback_query(lambda c: c.data in ("ing:submit:yes", "ing:submit:no"))
async def ingredients_submit(
    callback: CallbackQuery, session: AsyncSession, settings: Settings, state: FSMContext
) -> None:
    if callback.data == "ing:submit:no":
        await state.clear()
        await callback.message.answer("Скасовано.")
        await callback.answer()
        return

    data = await state.get_data()
    cart: list[dict] = list(data.get("cart") or [])
    if not cart:
        await callback.message.answer("Немає позицій для відправки.")
        await callback.answer()
        return

    client = await get_or_create_client(session, callback.from_user.id)
    payload = {"items": cart, "comment": data.get("comment")}
    order = await create_order(session, client_id=client.id, order_type=OrderType.ingredients, payload=payload)
    try:
        await send_order_to_group(callback.bot, settings, client=client, order=order)
    except Exception:
        # Group forwarding errors shouldn't block the user flow.
        pass
    else:
        await mark_order_sent(session, order.id)

    await state.clear()
    await callback.message.answer("Заявку створено. Менеджер скоро зв’яжеться з вами.")
    await callback.answer()

