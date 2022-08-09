from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    registration = State()
    login = State()
    user_id = State()
    password = State()
    start = State()
