"""MCP server tools"""

"""Main MCP server script"""

import os
import logging
import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Import tool registration functions
from . import google_search_tool
from . import memory_tools

# Load environment variables early
load_dotenv()

# Initialize MCP server
mcp = FastMCP("search")

# Register tools from separate modules
google_search_tool.register_tool(mcp)
memory_tools.register_tools(mcp)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    logging.info("Starting MCP server...")

    # Check for Google keys at startup (moved from google_search_tool.py)
    if not os.getenv("GOOGLE_API_KEY"):
        logging.warning(
            "GOOGLE_API_KEY environment variable not set. Google search tool will not work."
        )
    if not os.getenv("GOOGLE_CSE_ID"):
        logging.warning(
            "GOOGLE_CSE_ID environment variable not set. Google search tool will not work."
        )

    # Run the server
    mcp.run(transport="stdio")
