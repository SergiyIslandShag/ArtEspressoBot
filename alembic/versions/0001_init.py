"""init schema

Revision ID: 0001_init
Revises: 
Create Date: 2026-03-16

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column("is_regular", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "price_tier",
            sa.Enum("standard", "regular", name="price_tier"),
            server_default=sa.text("'standard'"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("telegram_id", name="uq_clients_telegram_id"),
    )
    op.create_index("ix_clients_telegram_id", "clients", ["telegram_id"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("ingredients", "service", name="order_type"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("new", "sent", "closed", name="order_status"),
            server_default=sa.text("'new'"),
            nullable=False,
        ),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("media", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_orders_client_id", "orders", ["client_id"])

    op.create_table(
        "prices",
        sa.Column("sku", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("unit", sa.String(length=64), nullable=True),
        sa.Column("standard_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("regular_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("prices")
    op.drop_index("ix_orders_client_id", table_name="orders")
    op.drop_table("orders")
    op.drop_index("ix_clients_telegram_id", table_name="clients")
    op.drop_table("clients")

    op.execute("DROP TYPE IF EXISTS order_status")
    op.execute("DROP TYPE IF EXISTS order_type")
    op.execute("DROP TYPE IF EXISTS price_tier")

