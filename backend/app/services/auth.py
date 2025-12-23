import os
from datetime import datetime, timedelta, UTC
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.app.database import get_db
from backend.app.models.user import User as UserORM

SECRET_KEY = os.getenv('SECRET_KEY').strip('"\'')
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

db_dependency = Annotated[AsyncSession, Depends(get_db)]


def create_access_token(login: str, user_id: int, expires_delta: timedelta):
    """
    Создает JWT access_token с login, user_id и временем истечения.

    Args:
        login: Логин пользователя (sub claim)
        user_id: ID пользователя (id claim)
        expires_delta: timedelta до истечения токена

    Returns:
        Закодированная JWT строка
    """
    encode = {
        'sub': login,
        'id': user_id
    }
    expires = datetime.now(UTC) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """
    Извлекает текущего пользователя из JWT токена.

    Args:
        token: Bearer токен из Authorization заголовка

    Returns:
        dict с 'username' и 'user_id'

    Raises:
        HTTPException: 401 при невалидном токене или отсутствии sub/id
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if user_id is None or username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")
        return {"username": username, 'user_id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


async def authenticate_user(login, password, db):
    """
    Аутентифицирует пользователя по логину и паролю.

    Args:
        login: Логин пользователя
        password: Пароль в plain text
        db: AsyncSession для запроса к БД

    Returns:
        UserORM объект при успешной аутентификации или False
    """
    query = select(UserORM).where(UserORM.login == login)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password_hash):
        return False
    return user
