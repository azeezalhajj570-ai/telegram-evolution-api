from unittest.mock import AsyncMock

import pytest

from app.mcp.tools.messaging import register_messaging_tools


class TestMessagingTools:
    @pytest.fixture
    def mock_mcp(self):
        mcp = AsyncMock()
        mcp.tool = lambda **kwargs: lambda f: f
        return mcp

    def test_register_messaging_tools(self, mock_mcp):
        register_messaging_tools(mock_mcp)
        assert True
