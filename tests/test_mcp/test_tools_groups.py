from unittest.mock import AsyncMock

import pytest

from app.mcp.tools.groups import register_group_tools


class TestGroupTools:
    @pytest.fixture
    def mock_mcp(self):
        mcp = AsyncMock()
        mcp.tool = lambda **kwargs: lambda f: f
        return mcp

    def test_register_group_tools(self, mock_mcp):
        register_group_tools(mock_mcp)
        assert True
