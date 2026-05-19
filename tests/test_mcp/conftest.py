import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.mcp.server import mcp_app


@pytest_asyncio.fixture
async def mcp_test_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=mcp_app.sse_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_instance_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def sample_chat_id() -> int:
    return 123456789
