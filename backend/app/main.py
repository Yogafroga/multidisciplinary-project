from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.auth import db_dependency
from backend.app.api import auth
from backend.app.api import uploadImage
from backend.app.api import uploadArchive
from backend.app.services.auth import get_current_user

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
# CORS

app.include_router(auth.router)
app.include_router(uploadImage.router)
app.include_router(uploadArchive.router)


@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {"user": user}


@app.get("/hello")
def hello():
    return {"message": "hello!"}


# дефолтная версия без корса
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from starlette import status
from backend.app.api.auth import db_dependency
from fastapi import FastAPI, HTTPException, Depends
from backend.app.api import auth
from backend.app.services.auth import get_current_user

user_dependency = Annotated[dict, Depends(get_current_user)]

app = FastAPI(title="CattleWeighAI API MVP", version="0.0.1")
app.include_router(auth.router)


@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {"user": user}


@app.get("/hello")
def hello():
    return {"message": "hello!"}
"""