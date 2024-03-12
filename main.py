from telebot import custom_filters

import models
from commands import register_functions as reg
import loader

if __name__ == "__main__":
    for func, kwargs in reg.functions_for_register:
        new_func = reg.register_func(loader.bot, func, **kwargs)

    loader.bot.add_custom_filter(custom_filters.StateFilter(loader.bot))

    models.create_models()

    print("Бот запустился!")
    loader.bot.polling(none_stop=True)
