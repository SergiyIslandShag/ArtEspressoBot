from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Client, Order, OrderStatus, OrderType, PriceTier


async def get_client_by_telegram_id(session: AsyncSession, telegram_id: int) -> Client | None:
    res = await session.execute(select(Client).where(Client.telegram_id == telegram_id))
    return res.scalar_one_or_none()


async def get_or_create_client(session: AsyncSession, telegram_id: int) -> Client:
    client = await get_client_by_telegram_id(session, telegram_id)
    if client:
        return client
    client = Client(telegram_id=telegram_id, price_tier=PriceTier.standard, is_regular=False)
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client


async def update_client_profile(session: AsyncSession, telegram_id: int, *, name: str | None, phone: str | None) -> Client:
    client = await get_or_create_client(session, telegram_id)
    if name is not None:
        client.name = name
    if phone is not None:
        client.phone = phone
    await session.commit()
    return client


async def create_order(
    session: AsyncSession,
    *,
    client_id: int,
    order_type: OrderType,
    payload: dict[str, Any],
    media: list[dict[str, Any]] | None = None,
) -> Order:
    order = Order(
        client_id=client_id,
        type=order_type,
        status=OrderStatus.new,
        payload=payload,
        media=media or [],
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def mark_order_sent(session: AsyncSession, order_id: int) -> None:
    res = await session.execute(select(Order).where(Order.id == order_id))
    order = res.scalar_one_or_none()
    if not order:
        return
    order.status = OrderStatus.sent
    await session.commit()


async def admin_search_clients(session: AsyncSession, query: str) -> list[Client]:
    q = (query or "").strip()
    if not q:
        return []
    if q.isdigit():
        telegram_id = int(q)
        res = await session.execute(select(Client).where(Client.telegram_id == telegram_id))
        row = res.scalar_one_or_none()
        return [row] if row else []

    like = f"%{q}%"
    res = await session.execute(
        select(Client).where(or_(Client.phone.ilike(like), Client.name.ilike(like))).order_by(Client.id.desc()).limit(10)
    )
    return list(res.scalars().all())


async def admin_set_client_regular(session: AsyncSession, client_id: int, is_regular: bool) -> Client | None:
    res = await session.execute(select(Client).where(Client.id == client_id))
    client = res.scalar_one_or_none()
    if not client:
        return None
    client.is_regular = is_regular
    await session.commit()
    return client


async def admin_set_client_price_tier(session: AsyncSession, client_id: int, tier: PriceTier) -> Client | None:
    res = await session.execute(select(Client).where(Client.id == client_id))
    client = res.scalar_one_or_none()
    if not client:
        return None
    client.price_tier = tier
    await session.commit()
    return client

