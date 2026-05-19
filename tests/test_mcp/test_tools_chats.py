from unittest.mock import AsyncMock

import pytest

from app.mcp.tools.chats import register_chat_tools


class TestChatTools:
    @pytest.fixture
    def mock_mcp(self):
        mcp = AsyncMock()
        mcp.tool = lambda **kwargs: lambda f: f
        return mcp

    def test_register_chat_tools(self, mock_mcp):
        register_chat_tools(mock_mcp)
        assert True
