from starlette.requests import Request

from backend.app import models


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
