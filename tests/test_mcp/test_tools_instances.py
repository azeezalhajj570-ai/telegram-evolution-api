from unittest.mock import AsyncMock

import pytest

from app.mcp.tools.instances import register_instance_tools


class TestInstanceTools:
    @pytest.fixture
    def mock_mcp(self):
        mcp = AsyncMock()
        mcp.tool = lambda **kwargs: lambda f: f
        return mcp

    def test_register_instance_tools(self, mock_mcp):
        register_instance_tools(mock_mcp)
        assert True
