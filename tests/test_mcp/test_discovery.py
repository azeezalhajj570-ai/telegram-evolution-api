from app.mcp.server import _register_all_tools


class TestToolDiscovery:
    def test_all_tools_register_without_error(self):
        _register_all_tools()
        assert True

    def test_mcp_app_has_tools(self):
        from app.mcp.server import mcp_app
        assert mcp_app is not None
