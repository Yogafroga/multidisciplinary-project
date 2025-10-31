import dotenv
from sqlalchemy.ext.asyncio import AsyncSession

dotenv.load_dotenv("C:/Users/lolke/PycharmProjects/multidisciplinary-project/backend/.env")
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
