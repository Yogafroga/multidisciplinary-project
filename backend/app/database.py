from peewee import *
import os
import dotenv

dotenv.load_dotenv()


def init_db() -> PostgresqlDatabase:
    """
    Устанавливает подключение к базе данных, используя данные из .env.
    :return: Объект PostgresqlDatabase
    """
    db = PostgresqlDatabase(
        os.getenv('DB_NAME'),
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD')
    )
    try:
        db.connect()
    except Exception as e:
        raise e
    return db
