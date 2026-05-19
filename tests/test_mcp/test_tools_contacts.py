from unittest.mock import AsyncMock

import pytest

from app.mcp.tools.contacts import register_contact_tools


class TestContactTools:
    @pytest.fixture
    def mock_mcp(self):
        mcp = AsyncMock()
        mcp.tool = lambda **kwargs: lambda f: f
        return mcp

    def test_register_contact_tools(self, mock_mcp):
        register_contact_tools(mock_mcp)
        assert True
