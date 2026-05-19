from app.mcp.server import _register_all_resources


class TestResources:
    def test_resources_register_without_error(self):
        _register_all_resources()
        assert True
