"""Memory Tools for MCP Server"""

import asyncio
import json
import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP

MEMORY_FILE = Path("data/memories.json")


async def add_memory(key: str, value: str) -> str:
    """Stores a piece of user-specific information (e.g., location, preference, fact) using a key-value pair.

    Use this tool to remember specific details. Provide a concise, descriptive 'key' (e.g., 'user_location', 'favorite_color', 'project_A_deadline') and the corresponding 'value'.
    **Crucially, if the user tells you their location or a key preference, store it immediately using a clear key like 'user_location'.** Good keys make lookup easier.

    Args:
        key: A short, descriptive identifier for the memory (use underscores for spaces).
        value: The actual information or context to be stored.
    """

    def save_sync():
        try:
            memories = {}
            if MEMORY_FILE.exists():
                MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    try:
                        loaded_data = json.load(f)
                        if isinstance(loaded_data, dict):
                            memories = loaded_data
                        else:
                            logging.warning(
                                "Memory file %s did not contain a dictionary. Resetting.",
                                MEMORY_FILE,
                            )
                    except json.JSONDecodeError:
                        logging.warning(
                            "Memory file %s is corrupted. Resetting.", MEMORY_FILE
                        )

            memories[key] = value

            MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(memories, f, indent=2)
            logging.info(
                "Saved memory to %s: Key='%s', Value='%s'", MEMORY_FILE, key, value
            )
            return f"Okay, I've remembered that '{key}' is '{value}'"

        except IOError as e:
            logging.exception("IOError while saving memory to %s: %s", MEMORY_FILE, e)
            return "Sorry, I encountered an error trying to save that memory."
        except Exception as e:  # pylint: disable=broad-except
            logging.exception(
                "Unexpected error while saving memory to %s: %s", MEMORY_FILE, e
            )
            return "Sorry, an unexpected error occurred while saving the memory."

    loop = asyncio.get_running_loop()
    result_str = await loop.run_in_executor(None, save_sync)
    return result_str


async def lookup_memories(query: str) -> str:
    """Searches stored memories (key-value pairs) for user-specific information (location, preferences, facts).

    **CRITICAL: ALWAYS use this tool FIRST before answering any question that references the user's personal context, location, preferences, or past statements.**
    Examples that MUST trigger this tool:
    - 'What is the weather where I live?' (Search query: 'user_location location address city')
    - 'What is my favorite color?' (Search query: 'favorite_color preference')
    - 'What did I tell you about project X?' (Search query: 'project X')
    - 'Do you remember my setup?' (Search query: 'setup configuration preferences')

    Do NOT answer questions about the user from your general knowledge. Check memory first using relevant keywords from the user's question. If you find relevant information, use it. If not, THEN you can state you don't have the memory stored.

    Args:
        query: Keywords derived from the user's question to search for within memory keys and values.
    """

    def lookup_sync():
        try:
            if not MEMORY_FILE.exists():
                return "I don't have any memories stored yet."

            memories = {}
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                try:
                    loaded_data = json.load(f)
                    if isinstance(loaded_data, dict):
                        memories = loaded_data
                    else:
                        logging.error(
                            "Memory storage %s is corrupted (not a dictionary). Cannot lookup.",
                            MEMORY_FILE,
                        )
                        return "Memory storage is corrupted (not a dictionary). Cannot lookup."
                except json.JSONDecodeError:
                    logging.error(
                        "Memory storage %s is corrupted (invalid JSON). Cannot lookup.",
                        MEMORY_FILE,
                    )
                    return "Memory storage is corrupted (invalid JSON). Cannot lookup."

            query_words = set(query.lower().split())
            if not query_words:
                return "Please provide keywords to search for in memories."

            found_items = []
            for key, value in memories.items():
                key_words = set(key.lower().split())
                value_str = str(value)
                value_words = set(value_str.lower().split())
                if query_words & key_words or query_words & value_words:
                    found_items.append(f"- {key}: {value}")

            if not found_items:
                return f"I couldn't find any memories in {MEMORY_FILE} where the key or value contained keywords from '{query}'."
            else:
                formatted_results = "\n".join(found_items)
                logging.info(
                    "Found %d memories in %s for query '%s'",
                    len(found_items),
                    MEMORY_FILE,
                    query,
                )
                return f"Here are the memories I found related to '{query}':\n{formatted_results}"
        except IOError as e:
            logging.exception(
                "IOError while looking up memory from %s: %s", MEMORY_FILE, e
            )
            return "Sorry, I encountered an error trying to access memories."
        except Exception as e:  # pylint: disable=broad-except
            logging.exception(
                "Unexpected error while looking up memory from %s: %s", MEMORY_FILE, e
            )
            return "Sorry, an unexpected error occurred while looking up memories."

    loop = asyncio.get_running_loop()
    result_str = await loop.run_in_executor(None, lookup_sync)
    return result_str


def register_tools(mcp_instance: FastMCP):
    """Registers the memory tools with the MCP instance."""
    mcp_instance.tool()(add_memory)
    mcp_instance.tool()(lookup_memories)
    logging.info("Registered add_memory and lookup_memories tools.")
