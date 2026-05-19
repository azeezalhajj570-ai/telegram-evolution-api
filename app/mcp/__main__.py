import logging
import os

from dotenv import load_dotenv

from app.mcp.auth import authenticate_stdio

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    api_key = os.environ.get("MCP_API_KEY", "")
    if api_key and not authenticate_stdio(api_key):
        logger.error("Invalid MCP_API_KEY configured — server will reject all tool calls")
    elif not api_key:
        logger.warning("No MCP_API_KEY set — authentication disabled (set MCP_API_KEY or API_KEYS)")

    from app.mcp.server import mcp_app

    logger.info("Starting MCP server with stdio transport")
    mcp_app.run(transport="stdio")


if __name__ == "__main__":
    main()
