from pydantic import BaseModel


class User(BaseModel):
    login: str
    password_hash: str


class CreateUser(BaseModel):
    login: str
    password: str
    role: int
