from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class RegistrationSG(StatesGroup):
    name = State()
    phone = State()


class IngredientsOrderSG(StatesGroup):
    choosing_item = State()
    entering_qty = State()
    comment = State()
    confirm = State()


class ServiceOrderSG(StatesGroup):
    choosing_service = State()
    machine_model = State()
    media = State()
    comment = State()
    confirm = State()


class AdminSG(StatesGroup):
    choosing_action = State()
    searching = State()

