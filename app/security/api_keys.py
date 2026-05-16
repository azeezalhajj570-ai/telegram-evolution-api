import secrets
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import ApiKey

_bearer = HTTPBearer(scheme_name="X-API-Key", auto_error=False)


def hash_api_key(plaintext: str) -> str:
    return bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt()).decode()


def verify_api_key(plaintext: str, key_hash: str) -> bool:
    return bcrypt.checkpw(plaintext.encode(), key_hash.encode())


def generate_api_key() -> str:
    return f"tev_{secrets.token_hex(24)}"


async def require_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    token = credentials.credentials
    result = await db.execute(select(ApiKey))
    for row in result.scalars():
        if verify_api_key(token, row.key_hash) and row.is_active:
            return token

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
