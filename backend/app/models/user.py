from peewee import CharField
from backend.app.database import BaseModel


class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
