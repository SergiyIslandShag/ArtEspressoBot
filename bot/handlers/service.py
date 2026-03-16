from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import Settings
from bot.db.models import OrderType
from bot.keyboards.common import skip_kb
from bot.keyboards.service import SERVICE_TYPES, service_media_kb, service_submit_kb, service_types_kb
from bot.services.db_ops import create_order, get_or_create_client, mark_order_sent
from bot.services.group_sender import send_order_to_group
from bot.states import ServiceOrderSG


router = Router(name=__name__)


def _title_for_service(code: str) -> str:
    for c, t in SERVICE_TYPES:
        if c == code:
            return t
    return code


@router.callback_query(lambda c: c.data == "menu:service")
async def service_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ServiceOrderSG.choosing_service)
    await state.update_data(media=[])
    await callback.message.answer("Оберіть тип сервісу:", reply_markup=service_types_kb())
    await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("svc:type:"))
async def service_choose_type(callback: CallbackQuery, state: FSMContext) -> None:
    code = callback.data.split(":", 2)[2]
    await state.update_data(service_type=code)
    await state.set_state(ServiceOrderSG.machine_model)
    await callback.message.answer("Введіть модель кавомашини (текстом).")
    await callback.answer()


@router.message(ServiceOrderSG.machine_model)
async def service_machine_model(message: Message, state: FSMContext) -> None:
    model = (message.text or "").strip()
    if not model:
        await message.answer("Будь ласка, введіть модель текстом.")
        return
    await state.update_data(machine_model=model)
    await state.set_state(ServiceOrderSG.media)
    await message.answer(
        "Додайте фото/відео (можна кілька). Коли завершите — натисніть «Готово».",
        reply_markup=service_media_kb(),
    )


@router.message(ServiceOrderSG.media)
async def service_collect_media(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    media: list[dict] = list(data.get("media") or [])

    if message.photo:
        file_id = message.photo[-1].file_id
        media.append({"type": "photo", "file_id": file_id})
    elif message.video:
        media.append({"type": "video", "file_id": message.video.file_id})
    else:
        await message.answer("Надішліть фото або відео, або натисніть «Готово».", reply_markup=service_media_kb())
        return

    await state.update_data(media=media)
    await message.answer(f"Додано ({len(media)}). Надішліть ще або натисніть «Готово».", reply_markup=service_media_kb())


@router.callback_query(lambda c: c.data == "svc:media:done")
async def service_media_done(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ServiceOrderSG.comment)
    await callback.message.answer("Додайте коментар (опційно).", reply_markup=skip_kb())
    await callback.answer()


@router.callback_query(lambda c: c.data == "flow:skip")
async def service_skip_comment(callback: CallbackQuery, state: FSMContext) -> None:
    if await state.get_state() != ServiceOrderSG.comment.state:
        await callback.answer()
        return
    await state.update_data(comment=None)
    await state.set_state(ServiceOrderSG.confirm)
    await _send_service_summary(callback.message, state)
    await callback.answer()


@router.message(ServiceOrderSG.comment)
async def service_comment(message: Message, state: FSMContext) -> None:
    comment = (message.text or "").strip()
    await state.update_data(comment=comment or None)
    await state.set_state(ServiceOrderSG.confirm)
    await _send_service_summary(message, state)


async def _send_service_summary(target: Message, state: FSMContext) -> None:
    data = await state.get_data()
    svc_code = data.get("service_type")
    machine_model = data.get("machine_model")
    media: list[dict] = list(data.get("media") or [])
    comment = data.get("comment")

    lines = [
        "Ваше замовлення (сервіс):",
        f"Тип: {_title_for_service(str(svc_code))}",
        f"Модель: {machine_model}",
        f"Медіа: {len(media)} файл(и)",
    ]
    if comment:
        lines.append(f"Коментар: {comment}")

    await target.answer("\n".join(lines), reply_markup=service_submit_kb())


@router.callback_query(lambda c: c.data in ("svc:submit:yes", "svc:submit:no"))
async def service_submit(callback: CallbackQuery, session: AsyncSession, settings: Settings, state: FSMContext) -> None:
    if callback.data == "svc:submit:no":
        await state.clear()
        await callback.message.answer("Скасовано.")
        await callback.answer()
        return

    data = await state.get_data()
    client = await get_or_create_client(session, callback.from_user.id)

    payload = {
        "service_type": data.get("service_type"),
        "service_type_title": _title_for_service(str(data.get("service_type"))),
        "machine_model": data.get("machine_model"),
        "comment": data.get("comment"),
    }
    media: list[dict] = list(data.get("media") or [])
    order = await create_order(session, client_id=client.id, order_type=OrderType.service, payload=payload, media=media)
    try:
        await send_order_to_group(callback.bot, settings, client=client, order=order)
    except Exception:
        pass
    else:
        await mark_order_sent(session, order.id)

    await state.clear()
    await callback.message.answer("Заявку створено. Менеджер скоро зв’яжеться з вами.")
    await callback.answer()

