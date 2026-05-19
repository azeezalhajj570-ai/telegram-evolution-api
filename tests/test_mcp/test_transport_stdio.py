import importlib


def test_stdio_entry_point_exists():
    try:
        importlib.import_module("app.mcp.__main__")
        assert True
    except ImportError:
        assert False, "app.mcp.__main__ module not found"
