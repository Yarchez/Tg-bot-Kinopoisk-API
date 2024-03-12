from telebot.handler_backends import State, StatesGroup


class MyState(StatesGroup):
    start = State()
    genre_low = State()
    count_low = State()
    genre_high = State()
    count_high = State()
    genre_custom = State()
    rating_custom = State()
    year_custom = State()
    count_custom = State()
