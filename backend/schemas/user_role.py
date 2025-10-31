from pydantic import BaseModel


class UserRole(BaseModel):
    role: str


class CreateUserRole(BaseModel):
    role: str
