import telebot.types as types
from peewee import IntegrityError

import States
import loader
import texts
import api_funcs
from models import Request, User

genres = api_funcs.get_genres()

keyboard_genres = types.ReplyKeyboardMarkup(resize_keyboard=True)
for i in range(0, len(genres) - 1, 3):
    genres_4 = [types.InlineKeyboardButton(genre) for genre in genres[i:i + 3]]
    if i == 30:
        genres_4 = [genres_4[0], types.InlineKeyboardButton(texts.BACK_MESSAGE), genres_4[-1]]
    keyboard_genres.add(*genres_4)

keyboard_count = types.ReplyKeyboardMarkup(resize_keyboard=True)

keyboard_count.add(types.InlineKeyboardButton(1), types.InlineKeyboardButton(5), types.InlineKeyboardButton(10))
keyboard_count.add(types.InlineKeyboardButton(texts.BACK_MESSAGE))


def start(message: types.Message):
    """метод запуска бота
    :param: сообщение от пользователя
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.first_name
    last_name = message.from_user.last_name

    try:
        user = User.create(
            user_id=user_id,
            username=username,
            last_name=last_name,
        )
        user.save()

        loader.bot.send_video(message.chat.id, texts.GREET_GIF, None, 'Text')
        loader.bot.send_message(message.chat.id, texts.START_MESSAGE.format(user=username), reply_markup=types.ReplyKeyboardRemove())
        loader.bot.set_state(user_id, States.MyState.start, chat_id)
    except IntegrityError:
        loader.bot.reply_to(message, f"Рад тебя снова видеть, {username}!", reply_markup=types.ReplyKeyboardRemove())


def cancel(message: types.Message):
    """
    метода отмена команды,
    при нажатии бот переходит в состояние start(в начало)
    :param message: сообщение от пользователя
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    state = loader.bot.get_state(user_id, chat_id)
    if state:
        loader.bot.set_state(user_id, States.MyState.start, chat_id)
        loader.bot.send_message(chat_id, texts.CANCEL_MESSAGE, reply_markup=types.ReplyKeyboardRemove())
    else:
        loader.bot.send_message(chat_id, texts.NOT_IN_PROGRESS_MESSAGE, reply_markup=types.ReplyKeyboardRemove())


def low(message: types.Message):
    """
    функция срабатывающая при вводе команды low, выводит пользователю список жанров для выбора
    устанавливает состояние genre_low
    :param message:сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    loader.bot.send_message(chat_id, texts.LOW_MESSAGE, reply_markup=keyboard_genres)
    loader.bot.set_state(user_id, States.MyState.genre_low, chat_id)


def get_count(message: types.Message):
    """
    get_count срабатывает после функции low. Функция сохраняет выбор жанра пользователем через bot.retrieve_data,
     устанавливает состояние count_low и предлагает выбрать кол-во выдаваемых результатов
    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_text = message.text

    if user_text == texts.BACK_MESSAGE:
        cancel(message)
        return

    loader.bot.send_message(chat_id, f'Вы выбрали {user_text}!', reply_markup=types.ReplyKeyboardRemove())

    genre_user = message.text.lower()
    loader.bot.set_state(user_id, States.MyState.count_low, chat_id)
    with loader.bot.retrieve_data(user_id, chat_id) as data:
        data["genre"] = genre_user
    loader.bot.send_message(
        chat_id, texts.COUNT_MESSAGE, reply_markup=keyboard_count
    )


def show_low(message: types.Message):
    """
    Функция выдачи результатов для команды low.
    срабатывает после get_count, делает запрос к API c указанными пользователем жанром и кол-вом.
    Записывает информацию о запросе пользователя в базу данных
    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    count = message.text

    if count == texts.BACK_MESSAGE:
        cancel(message)
        return

    with loader.bot.retrieve_data(user_id, chat_id) as data:
        genre_user = data["genre"]

    res = api_funcs.send_req(rating="1", genre=genre_user, count=count, rate_imdb="1-6", year="1874-2050")
    if res is None:
        loader.bot.send_video(chat_id, texts.FAIL_GIF, None, 'Text')
        loader.bot.send_message(chat_id, 'Не удалось выполнить поиск', reply_markup=types.ReplyKeyboardRemove())
    else:
        result = api_funcs.format_data(res)
        loader.bot.send_video(chat_id, texts.SUCCESS_GIF, None, 'Text')
        loader.bot.send_message(chat_id,
                                texts.RESULT_MESSAGE.format(user=message.from_user.first_name),
                                reply_markup=types.ReplyKeyboardRemove())
        for elem in result:
            loader.bot.send_message(chat_id, "".join(elem), parse_mode="Markdown")
        user = User.get(User.user_id == user_id)

        new_request = Request(genre=data["genre"], user=user, count=count)
        new_request.save()

        loader.bot.delete_state(user_id, chat_id)


def high(message: types.Message):
    """
    функция срабатывающая при вводе команды high, выводит пользователю список жанров для выбора
    устанавливает состояние genre_high
    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    loader.bot.set_state(user_id, States.MyState.genre_high, chat_id)

    loader.bot.send_message(
        chat_id, texts.LOW_MESSAGE, reply_markup=keyboard_genres
    )


def get_count_high(message: types.Message):
    """
    get_count_high срабатывает после функции high. Функция сохраняет выбор жанра пользователем через bot.retrieve_data,
     устанавливает состояние count_high и предлагает выбрать кол-во выдаваемых результатов
    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    loader.bot.send_message(message.chat.id, f'Вы выбрали {message.text}!', reply_markup=types.ReplyKeyboardRemove())

    genre_user = message.text.lower()
    with loader.bot.retrieve_data(user_id, chat_id) as data:
        data["genre"] = genre_user
    loader.bot.set_state(user_id, States.MyState.count_high, chat_id)

    loader.bot.send_message(
        chat_id, texts.COUNT_MESSAGE, reply_markup=keyboard_count
    )


def show_high(message: types.Message):
    """
    Функция выдачи результатов для команды high.
    срабатывает после get_count_high, делает запрос к API c указанными пользователем жанром и кол-вом.
    Записывает информацию о запросе пользователя в базу данных
    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    with loader.bot.retrieve_data(user_id, chat_id) as data:
        genre_user = data["genre"]
    count = message.text
    res = api_funcs.send_req(rating="1", genre=genre_user, count=count, rate_imdb="6-10", year="1874-2050")
    if res is None:
        loader.bot.send_video(chat_id, texts.FAIL_GIF, None, 'Text')
        loader.bot.send_message(chat_id, 'Не удалось выполнить поиск', reply_markup=types.ReplyKeyboardRemove())
    else:
        result = api_funcs.format_data(res)
        loader.bot.send_video(chat_id, texts.SUCCESS_GIF, None, 'Text')
        loader.bot.send_message(chat_id,
                                texts.RESULT_MESSAGE.format(user=message.from_user.first_name),
                                reply_markup=types.ReplyKeyboardRemove())
        for elem in result:
            loader.bot.send_message(chat_id, "".join(elem), parse_mode="Markdown")
        user = User.get(User.user_id == user_id)

        new_request = Request(genre=data["genre"], user=user, count=count)
        new_request.save()

        loader.bot.delete_state(user_id, chat_id)


def custom(message: types.Message):
    """
    функция срабатывающая при вводе команды custom, выводит пользователю список жанров для выбора
    устанавливает состояние genre_custom
    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    loader.bot.set_state(user_id, States.MyState.genre_custom, chat_id)

    loader.bot.send_message(
        chat_id, texts.CUSTOM_MESSAGE, reply_markup=keyboard_genres
    )


def get_rating(message: types.Message):
    """
    срабатывает после функции custom, функция сохраняет выбор жанра пользователем через bot.retrieve_data,
     устанавливает состояние rating_custom, предлагает выбрать рейтинг/диапазон
    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    loader.bot.send_message(message.chat.id,
                            f'Вы выбрали {message.text}!',
                            reply_markup=types.ReplyKeyboardRemove())

    genre_user = message.text.lower()
    with loader.bot.retrieve_data(user_id, chat_id) as data:
        data["genre"] = genre_user
    loader.bot.set_state(user_id, States.MyState.rating_custom, chat_id)

    loader.bot.send_message(chat_id, texts.RATING_MESSAGE)


def get_year(message: types.Message):
    """
    срабатывает после get_rating, функция сохраняет выбор рейтинга пользователем через bot.retrieve_data,
    утснавливает состояние year_custom, предлагает выбрать временной промежуток для поиска
    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    rating_user = message.text.lower()
    with loader.bot.retrieve_data(user_id, chat_id) as data:
        data["rating"] = rating_user
    loader.bot.set_state(user_id, States.MyState.year_custom, chat_id)

    loader.bot.send_message(chat_id, texts.YEAR_MESSAGE)


def get_count_custom(message: types.Message):
    """
    срабатывает после get_year, сохраняет выбор года через bot.retrieve_data,
    устанавливает состояние count_custom
    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    year_user = message.text.lower()
    with loader.bot.retrieve_data(user_id, chat_id) as data:
        data["year"] = year_user
    loader.bot.set_state(user_id, States.MyState.count_custom, chat_id)

    loader.bot.send_message(chat_id,
                            texts.COUNT_MESSAGE,
                            reply_markup=keyboard_count)


def show_custom(message: types.Message):
    """
    Функция выдачи пользователю результатов для команды custom.
    срабатывает после get_count_custom, получает данные через retrieve_data,
    делает запрос к API c введенными пользователем жанром, рейтингом, годом и кол-вом.
     Записывает информацию о запросе в базу данных
    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    with loader.bot.retrieve_data(user_id, chat_id) as data:
        genre_user = data["genre"]
        rating_user = data["rating"]
        year_user = data["year"]
    count = message.text.lower()
    res = api_funcs.send_req(rating="1", genre=genre_user, count=count, rate_imdb=rating_user, year=year_user)
    if res is None:
        loader.bot.send_video(chat_id, texts.FAIL_GIF, None, 'Text', reply_markup=types.ReplyKeyboardRemove())
        loader.bot.send_message(chat_id, 'Не удалось выполнить поиск')
    else:
        result = api_funcs.format_data(res)
        loader.bot.send_video(chat_id, texts.SUCCESS_GIF, None, 'Text')
        loader.bot.send_message(chat_id,
                                texts.RESULT_MESSAGE.format(user=message.from_user.first_name),
                                reply_markup=types.ReplyKeyboardRemove())
        for elem in result:
            loader.bot.send_message(chat_id, "".join(elem), parse_mode="Markdown")
        user = User.get(User.user_id == user_id)

        new_request = Request(genre=genre_user, user=user, count=count, rating=rating_user, year=year_user)
        new_request.save()

        loader.bot.delete_state(user_id, chat_id)


def show_history(message: types.Message):
    """
    Метод для вывода запросов из базы данных по команде history.
    :param message: сообщение от пользователя
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    history = Request.select().where(Request.user_id == user_id).order_by(Request.created_at.desc()).limit(10)
    for his in reversed(history):
        loader.bot.send_message(chat_id, his, parse_mode="Markdown")