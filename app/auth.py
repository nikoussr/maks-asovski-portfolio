from itsdangerous import URLSafeSerializer, BadSignature
from fastapi import Request
from .config import settings

_serializer = URLSafeSerializer(settings.secret_key)


def create_session_token(username: str) -> str:
    return _serializer.dumps({"user": username})


def verify_session_token(token: str) -> str | None:
    try:
        data = _serializer.loads(token)
        return data.get("user")
    except (BadSignature, Exception):
        return None


def is_authenticated(request: Request) -> bool:
    token = request.cookies.get("admin_session")
    if not token:
        return False
    return verify_session_token(token) is not None
