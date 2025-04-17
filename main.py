"""MCP server tools"""

import os
import asyncio
import logging
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

mcp = FastMCP("search")

load_dotenv()

USER_AGENT = "weather-app/1.0"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
MEMORY_FILE = Path("memories.json")

# Check if Google keys are available
if not GOOGLE_API_KEY:
    print(
        "Warning: GOOGLE_API_KEY environment variable not set. Google search tool will not work."
    )
if not GOOGLE_CSE_ID:
    print(
        "Warning: GOOGLE_CSE_ID environment variable not set. Google search tool will not work."
    )


@mcp.tool()
async def google_search(query: str) -> str:
    """Searches the public web using Google for current information, facts, or external resources.

    Consider using this tool whenever the user asks a question where up-to-date information might be helpful,
    or if the answer is likely found outside your internal knowledge base. Also useful for checking facts
    or finding specific URLs or details.

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
            logging.info("Search results: %s", output)
            return output.strip()

        except HttpError as e:
            logging.exception("An HTTP error occurred during Google search: %s", e)
            return f"Error performing search: {e.resp.status} {e.resp.reason}"
        except Exception as e:
            logging.exception(
                "An unexpected error occurred during Google search: %s", e
            )
            return "An unexpected error occurred during the search."

    loop = asyncio.get_running_loop()
    result_str = await loop.run_in_executor(None, search_sync)
    return result_str


# --- Memory Tools ---


@mcp.tool()
async def add_memory(key: str, value: str) -> str:
    """Stores a piece of user-specific information, fact, preference, or context using a key-value pair.

    Use this tool to remember specific details. Provide a concise, descriptive 'key' (e.g., 'favorite_color',
    'project_A_deadline', 'preferred_language') and the corresponding 'value' (e.g., 'blue', '2024-12-31',
    'Python'). Good keys make lookup easier. Store context proactively when it seems relevant for future interactions.

    Args:
        key: A short, descriptive identifier for the memory (use underscores for spaces).
        value: The actual information or context to be stored.
    """

    def save_sync():
        try:
            memories = {}
            if MEMORY_FILE.exists():
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    try:
                        loaded_data = json.load(f)
                        # Ensure we have a dictionary
                        if isinstance(loaded_data, dict):
                            memories = loaded_data
                        else:
                            logging.warning("Memory file did not contain a dictionary. Resetting.")
                    except json.JSONDecodeError:
                        logging.warning("Memory file is corrupted. Resetting.")
            
            memories[key] = value # Add or update the key-value pair
            
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(memories, f, indent=2)
            logging.info("Saved memory: Key='%s', Value='%s'", key, value)
            return f"Okay, I've remembered that '{key}' is '{value}'"

        except IOError as e:
            logging.exception("IOError while saving memory: %s", e)
            return "Sorry, I encountered an error trying to save that memory."
        except Exception as e:
            logging.exception("Unexpected error while saving memory: %s", e)
            return "Sorry, an unexpected error occurred while saving the memory."

    loop = asyncio.get_running_loop()
    result_str = await loop.run_in_executor(None, save_sync)
    return result_str


@mcp.tool()
async def lookup_memories(query: str) -> str:
    """Searches stored memories (key-value pairs) for relevant user-specific information.

    Searches for the query keywords within both the memory keys and their corresponding values.
    Use this tool BEFORE answering questions about the user's preferences, past statements, or personal context.
    If the user asks 'What is my X?', 'Do you remember Y?', 'What did I tell you about Z?', or anything that refers
    to potentially stored user information, call this tool first with relevant keywords.

    Args:
        query: The keywords or phrase to search for within memory keys and values.
    """

    def lookup_sync():
        try:
            if not MEMORY_FILE.exists():
                return "I don't have any memories stored yet."

            memories = {}
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                try:
                    loaded_data = json.load(f)
                    if isinstance(loaded_data, dict):
                        memories = loaded_data
                    else:
                         return "Memory storage is corrupted (not a dictionary). Cannot lookup."
                except json.JSONDecodeError:
                    return "Memory storage is corrupted (invalid JSON). Cannot lookup."

            query_words = set(query.lower().split())
            if not query_words:
                return "Please provide keywords to search for in memories."

            found_items = []
            for key, value in memories.items():
                key_words = set(key.lower().split())
                # Ensure value is treated as string for splitting
                value_str = str(value) 
                value_words = set(value_str.lower().split())
                
                # Check if ANY query word overlaps with key OR value words (using set intersection)
                if query_words & key_words or query_words & value_words:
                    found_items.append(f"- {key}: {value}")

            if not found_items:
                return f"I couldn't find any memories where the key or value contained keywords from '{query}'."
            else:
                formatted_results = "\n".join(found_items)
                logging.info(
                    "Found %d memories for query '%s'", len(found_items), query
                )
                return f"Here are the memories I found related to '{query}':\n{formatted_results}"
        except IOError as e:
            logging.exception("IOError while looking up memory: %s", e)
            return "Sorry, I encountered an error trying to access memories."
        except Exception as e:
            logging.exception("Unexpected error while looking up memory: %s", e)
            return "Sorry, an unexpected error occurred while looking up memories."

    loop = asyncio.get_running_loop()
    result_str = await loop.run_in_executor(None, lookup_sync)
    return result_str


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    logging.info("Starting MCP server...")
    mcp.run(transport="stdio")
