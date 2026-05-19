from app.mcp.server import _register_all_prompts


class TestPrompts:
    def test_prompts_register_without_error(self):
        _register_all_prompts()
        assert True
