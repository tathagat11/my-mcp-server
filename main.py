"""Main MCP server script"""

import os
import logging
import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

import src.google_search_tool
import src.memory_tools


load_dotenv()

mcp = FastMCP("search")

src.google_search_tool.register_tool(mcp)
src.memory_tools.register_tools(mcp)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    logging.info("Starting MCP server...")

    if not os.getenv("GOOGLE_API_KEY"):
        logging.warning(
            "GOOGLE_API_KEY environment variable not set. Google search tool will not work."
        )
    if not os.getenv("GOOGLE_CSE_ID"):
        logging.warning(
            "GOOGLE_CSE_ID environment variable not set. Google search tool will not work."
        )

    mcp.run(transport="stdio")
