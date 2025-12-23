from datetime import timedelta

from fastapi import Depends, status, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from backend.app.database import get_db
from backend.app.services.auth import db_dependency, bcrypt_context, authenticate_user, create_access_token
from backend.schemas.token import Token

from backend.schemas.user import CreateUser
from backend.app.models.user import User as UserORM
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUser):
    """
    Создает нового пользователя в системе.

    Args:
        db: AsyncSession для сохранения пользователя
        create_user_request: CreateUser схема с login, password, role

    Returns:
        Словарь с сообщением "User created successfully."

    Примечание:
        Пароль хешируется bcrypt_context.hash() перед сохранением
        Возвращается refresh после commit для получения ID
    """
    create_user_model = UserORM(login=create_user_request.login,
                                password_hash=bcrypt_context.hash(create_user_request.password),
                                role_id=create_user_request.role)

    db.add(create_user_model)
    await db.commit()
    await db.refresh(create_user_model)
    return {"message": "User created successfully."}


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: AsyncSession = Depends(get_db)):
    """
    Аутентифицирует пользователя и выдает JWT access_token

    Args:
        form_data: OAuth2PasswordRequestForm с username/password
        db: AsyncSession для аутентификации через authenticate_user

    Returns:
        Token с access_token и token_type="bearer"

    Raises:
        HTTPException: 401 если неверные учетные данные

    Примечание:
        Токен содержит login и user_id, срок действия 30 дней
    """
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    token = create_access_token(user.login, user.id, timedelta(minutes=43200))
    return {"access_token": token, "token_type": "bearer"}
