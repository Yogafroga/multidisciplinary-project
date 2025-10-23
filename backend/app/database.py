from peewee import *
import os
import dotenv

dotenv.load_dotenv()

DATABASE = PostgresqlDatabase(
    os.getenv('DB_NAME'),
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USERNAME'),
    password=os.getenv('DB_PASSWORD')
)


class BaseModel(Model):
    class Meta:
        database = DATABASE


def init_db() -> PostgresqlDatabase:
    """
    Устанавливает подключение к базе данных, используя данные из .env.
    :return: Объект PostgresqlDatabase
    """
    try:
        DATABASE.connect()
    except Exception as e:
        raise e
    return DATABASE
