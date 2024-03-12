import locale


from peewee import (
    CharField,
    ForeignKeyField,
    DateTimeField,
    IntegerField,
    Model,
    SqliteDatabase,
)

import datetime

from config_data.my_config import DB_PATH

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    username = CharField()
    last_name = CharField(null=True)


class Request(BaseModel):
    request_id = IntegerField(primary_key=True)
    user = ForeignKeyField(User)
    genre = CharField()
    rating = CharField(null=True)
    year = CharField(null=True)
    count = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        text = (
            f"Жанр: {self.genre}\n"
            f"Рейтинг: {'Не указан' if self.rating is None else self.rating}\n"
            f"Год: {'Не указан' if self.year is None else self.year}\n"
            f"Количество: {self.count}\n"
            f"Дата запроса: {self.created_at.strftime('%d %B %H:%M')}\n"
        )
        return text


def create_models():
    db.create_tables(BaseModel.__subclasses__())
