from pydantic import BaseModel


class User(BaseModel):
    id: int
    login: str
    password_hash: str
