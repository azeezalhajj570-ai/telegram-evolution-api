import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.database import Base, get_db
from app.db.models import ApiKey
from app.main import app
from app.security.api_keys import hash_api_key

_test_engine = create_async_engine("sqlite+aiosqlite://", echo=False)
_test_async_session = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _override_get_db() -> AsyncGenerator:
    async with _test_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = _override_get_db


@pytest_asyncio.fixture
async def api_key_token() -> str:
    token = "test-api-key-for-testing"
    async with _test_async_session() as session:
        session.add(ApiKey(name="test", key_hash=hash_api_key(token), is_active=True))
        await session.commit()
    return token


@pytest_asyncio.fixture
async def client(api_key_token: str) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {api_key_token}"}
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        yield ac
