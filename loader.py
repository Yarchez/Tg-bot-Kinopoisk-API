import telebot
from telebot.types import BotCommand

from config_data.my_config import BOT_TOKEN


state_storage = telebot.storage.StateMemoryStorage()
bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)


DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('cancel', "Отменить команду и вернуться в начало"),
    ('low', 'Поиск по жанру с низким рейтингом'),
    ('high', 'Поиск по жанру с высоким рейтингом'),
    ('custom', 'Настройка поиска'),
    ('history', 'История поиска')
)


bot.set_my_commands(
    [BotCommand(*i) for i in DEFAULT_COMMANDS]
)
