# Telegram Bot Movie Search

Проект представляет собой бота для поиска фильмов,сериалов итд
с помощью API Кинопоиска. 

### Команды
- /start запуск бота
- /cancel отмена команды/возвращение в начало
- /low поиск по низкому рейтингу
- /high поиск по высокому рейтингу
- /custom поиск с настройками
- /history вывод запросов из базы данных


### Установка и настройка:
1. Клонируйте репозиторий

2. Установите зависимости:
``
pip install -r requirements.txt
`` 

3. Создайте бота в телеграм через BotFather. Получите доступ к API Кинопоиска
``
https://kinopoisk.dev/#api
``

4. Настройка переменных окружения: В файле .env_example укажите свой токен бота и токен Кинопоиска.

5. Запустите бота:
``
python main.py
``
