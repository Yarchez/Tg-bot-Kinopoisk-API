from config_data.my_config import API_TOKEN

import requests


def send_req(rating: str, genre: str, count: str, rate_imdb: str, year: str):
    """
    Метод для запроса к API
    :param rating:
    :param genre:
    :param count:
    :param rate_imdb:
    :param year:
    :return:список объектов, каждый из которых представлен словарем
    """
    url = "https://api.kinopoisk.dev/v1.4/movie"
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_TOKEN,
    }

    sort_type = "1" if rating == "1" else "-1"

    params = {
        "limit": count,
        "genres.name": genre,
        "sortField": "rating.imdb",
        "sortType": sort_type,
        "notNullFields": ["name", "poster.url", "year", "rating.imdb", "rating.kp"],
        "selectFields": ["poster", "name", "type", "year", "rating", "genres", "id"],
        "rating.imdb": rate_imdb,
        "rating.kp": "1-10",
        "year": year
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    movies_api = response.json()
    return movies_api["docs"]


def format_data(data: dict):
    """
    Метод для форматирования ответа от API для отправки ботом пользователю
    :param data:
    :return: отформатированный список рез-ов
    """
    formatted_data = []
    for movie in data:
        name = movie["name"]
        type_movie = movie["type"]
        year = movie["year"]
        rating_kp = movie["rating"]['kp']
        rating_imdb = movie["rating"]['imdb']
        id = movie["id"]
        genres = ", ".join(g["name"] for g in movie["genres"])
        url = movie["poster"]["url"]

        formatted_data.append(
            f"{name}({year})- {genres}; тип: {type_movie}; рейтинги: Кинопоиск-{rating_kp}, IMDB-{rating_imdb};"
            f" id: {id}\n{url}"
        )
    return formatted_data


def get_genres():
    """
    Метод запроса к API для получения жанров
    :return: список жанров
    """
    url = "https://api.kinopoisk.dev/v1/movie/possible-values-by-field?field=genres.name"

    headers = {"accept": "application/json", "X-API-KEY": API_TOKEN}

    req_api = requests.get(url, headers=headers)
    response_genres = req_api.json()
    formatted_data = []
    formatted_data.extend(f"{item['name'].capitalize()}" for item in response_genres)
    return formatted_data
