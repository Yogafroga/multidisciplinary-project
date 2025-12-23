from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from backend.app.api.auth import db_dependency
from fastapi import FastAPI, HTTPException, Depends
from backend.app.api import auth, uploadArchive, uploadImage, reports, batches, history
from backend.app.services.auth import get_current_user
from backend.app.core.logging_config import setup_logging, get_logger

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
