import time
from typing import Any, Optional

import jwt

from app.config import settings

ALGORITHM = "HS256"
_DEFAULT_SECRET = "change-me-in-production-use-a-strong-random-secret"


def _get_secret() -> str:
    return settings.jwt_secret or _DEFAULT_SECRET


def create_token(
    sub: str,
    tenant_id: str = "",
    role: str = "user",
    permissions: Optional[list[str]] = None,
    ttl: Optional[int] = None,
) -> str:
    """Create a signed JWT access token."""
    now = int(time.time())
    payload: dict[str, Any] = {
        "sub": sub,
        "iat": now,
        "exp": now + (ttl or settings.jwt_ttl),
    }
    if tenant_id:
        payload["tenant_id"] = tenant_id
    if role:
        payload["role"] = role
    if permissions:
        payload["permissions"] = permissions
    return jwt.encode(payload, _get_secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """Decode and validate a JWT token. Returns None if invalid or expired."""
    try:
        payload = jwt.decode(token, _get_secret(), algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
