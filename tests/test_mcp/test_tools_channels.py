from unittest.mock import AsyncMock

import pytest

from app.mcp.tools.channels import register_channel_tools


class TestChannelTools:
    @pytest.fixture
    def mock_mcp(self):
        mcp = AsyncMock()
        mcp.tool = lambda **kwargs: lambda f: f
        return mcp

    def test_register_channel_tools(self, mock_mcp):
        register_channel_tools(mock_mcp)
        assert True
