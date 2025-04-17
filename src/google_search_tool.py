"""Google Search Tool for MCP Server"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mcp.server.fastmcp import FastMCP


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")


async def google_search(query: str) -> str:
    """Searches the public web using Google for current information, facts, or external resources.

    Use this tool when the user asks a question where up-to-date information might be helpful,
    or if the answer is likely found outside your internal knowledge base.

    Args:
        query: The keywords or question to search for on Google.
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return "Google Search tool is not configured. Missing API key or CSE ID."

    def search_sync():
        try:
            service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
            result = (
                service.cse()  # pylint: disable=no-member
                .list(q=query, cx=GOOGLE_CSE_ID, num=5)
                .execute()
            )
            search_items = result.get("items", [])
            if not search_items:
                return "No results found."

            output = f"Search results for '{query}':\n\n"
            for i, item in enumerate(search_items):
                title = item.get("title", "No Title")
                link = item.get("link", "#")
                snippet = item.get("snippet", "No Snippet").replace("\n", " ")
                output += f"{i+1}. {title}\n   Link: {link}\n   Snippet: {snippet}\n\n"
            return output.strip()

        except HttpError as e:
            logging.exception("An HTTP error occurred during Google search: %s", e)
            return f"Error performing search: {e.resp.status} {e.resp.reason}"
        except Exception as e: # pylint: disable=broad-except
            logging.exception(
                "An unexpected error occurred during Google search: %s", e
            )
            return "An unexpected error occurred during the search."

    loop = asyncio.get_running_loop()
    result_str = await loop.run_in_executor(None, search_sync)
    return result_str


def register_tool(mcp_instance: FastMCP):
    """Registers the google_search tool with the MCP instance."""
    if not GOOGLE_API_KEY:
        logging.warning(
            "GOOGLE_API_KEY environment variable not set. Google search tool will not be registered."
        )
    elif not GOOGLE_CSE_ID:
        logging.warning(
            "GOOGLE_CSE_ID environment variable not set. Google search tool will not be registered."
        )
    else:
        mcp_instance.tool()(google_search)
        logging.info("Registered google_search tool.")
