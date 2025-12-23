from starlette.requests import Request
from starlette.responses import Response

from backend.app.database import async_session_maker
from backend.app.main import app
from backend.app.middleware.audit import store_audit_middleware


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
