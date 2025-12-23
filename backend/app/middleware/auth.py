import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from backend.app.services.auth import SECRET_KEY


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
