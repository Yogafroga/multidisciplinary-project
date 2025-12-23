from typing import Annotated

import jwt
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from backend.app.api.auth import db_dependency
from fastapi import FastAPI, HTTPException, Depends
from backend.app.api import auth, uploadArchive, uploadImage, reports, batches, history
from backend.app import models
from backend.app.database import async_session_maker
from backend.app.services.auth import get_current_user, SECRET_KEY
from backend.app.core.logging_config import setup_logging, get_logger
from fastapi import Response
from fastapi.requests import Request

# Настройка логирования при старте приложения
setup_logging(log_level="INFO")

logger = get_logger(__name__)

user_dependency = Annotated[dict, Depends(get_current_user)]

app = FastAPI(title="CattleWeighAI API MVP", version="0.0.1")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vue dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth.router)
app.include_router(uploadArchive.router)
app.include_router(uploadImage.router)
app.include_router(history.router)
app.include_router(reports.router)
app.include_router(batches.router)

logger.info("FastAPI application initialized")


@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    logger.debug(f"Root endpoint accessed by user: {user.get('user_id') if user else None}")
    if user is None:
        logger.warning("Unauthorized access attempt to root endpoint")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {"user": user}


@app.get("/hello")
def hello():
    logger.debug("Hello endpoint accessed")
    return {"message": "hello!"}


# Middleware для установки пользователя
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Пытаемся получить пользователя из токена
        auth_header = request.headers.get("Authorization")
        request.state.user_id = None  # По умолчанию None для анонимных запросов

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                request.state.user_id = payload.get("id")
            except jwt.InvalidTokenError:
                pass  # Оставляем None

        response = await call_next(request)
        return response


app.add_middleware(AuthMiddleware)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = async_session_maker()
        response = await call_next(request)
        response_body = b''

        if all(f not in str(request.url) for f in ['docs', 'openapi.json', 'favicon.ico']):
            async for chunk in response.body_iterator:
                response_body += chunk
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            await store_audit_middleware(request, response_body, request.state.db)
    finally:
        await request.state.db.close()
    return response


async def store_audit_middleware(request: Request, response_body, db):
    audit_entry = models.Audit()
    audit_entry.user_id = getattr(request.state, "user_id", None)
    audit_entry.url = str(request.url)
    audit_entry.headers = [f"{k}: {v}" for k, v in request.headers.items()]
    audit_entry.method = request.method
    try:
        audit_entry.response = response_body.decode('utf-8')
    except UnicodeDecodeError:
        audit_entry.response = f"<binary data: {len(response_body)} bytes>"

    db.add(audit_entry)
    await db.commit()
