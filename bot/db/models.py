from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.base import Base


class PriceTier(str, enum.Enum):
    standard = "standard"
    regular = "regular"


class OrderType(str, enum.Enum):
    ingredients = "ingredients"
    service = "service"


class OrderStatus(str, enum.Enum):
    new = "new"
    sent = "sent"
    closed = "closed"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)

    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)

    is_regular: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    price_tier: Mapped[PriceTier] = mapped_column(
        Enum(PriceTier, name="price_tier"),
        nullable=False,
        server_default=PriceTier.standard.value,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    orders: Mapped[list["Order"]] = relationship(back_populates="client")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), index=True, nullable=False)

    type: Mapped[OrderType] = mapped_column(Enum(OrderType, name="order_type"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        nullable=False,
        server_default=OrderStatus.new.value,
    )

    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")
    media: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, server_default="[]")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    client: Mapped["Client"] = relationship(back_populates="orders")


class Price(Base):
    __tablename__ = "prices"

    sku: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(64), nullable=True)

    standard_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    regular_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

