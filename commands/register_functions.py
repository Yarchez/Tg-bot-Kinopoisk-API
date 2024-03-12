import telebot

from commands import bot_funcs
import States

import functools


def register_func(bot: telebot.TeleBot, func, *args, **kwargs):
    """
    Метод декорирования функций бота
    :param bot:
    :param func:
    :param args:
    :param kwargs:
    :return:
    """
    @bot.message_handler(*args, **kwargs)
    @functools.wraps(func)
    def wrapper(message):
        return func(message)

    return wrapper


functions_for_register = (
    (bot_funcs.show_history, {"commands": ["history"]}),
    (bot_funcs.start, {"commands": ["start"]}),
    (bot_funcs.cancel, {"commands": ["cancel"]}),
    (bot_funcs.low, {"commands": ["low"]}),
    (bot_funcs.get_count, {"state": States.MyState.genre_low}),
    (bot_funcs.show_low, {"state": States.MyState.count_low}),
    (bot_funcs.high, {"commands": ["high"]}),
    (bot_funcs.get_count_high, {"state": States.MyState.genre_high}),
    (bot_funcs.show_high, {"state": States.MyState.count_high}),
    (bot_funcs.custom, {"commands": ["custom"]}),
    (bot_funcs.get_rating, {"state": States.MyState.genre_custom}),
    (bot_funcs.get_year, {"state": States.MyState.rating_custom}),
    (bot_funcs.get_count_custom, {"state": States.MyState.year_custom}),
    (bot_funcs.show_custom, {"state": States.MyState.count_custom}),
)
