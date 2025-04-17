"""Memory Tools for MCP Server"""

import asyncio
import json
import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP

MEMORY_FILE = Path("memories.json")

# --- Memory Tools ---

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
                # Ensure the parent directory exists (though it should in this case)
                MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    try:
                        loaded_data = json.load(f)
                        # Ensure we have a dictionary
                        if isinstance(loaded_data, dict):
                            memories = loaded_data
                        else:
                            logging.warning("Memory file %s did not contain a dictionary. Resetting.", MEMORY_FILE)
                    except json.JSONDecodeError:
                        logging.warning("Memory file %s is corrupted. Resetting.", MEMORY_FILE)
            
            memories[key] = value # Add or update the key-value pair
            
            # Ensure the parent directory exists before writing
            MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(memories, f, indent=2)
            logging.info("Saved memory to %s: Key='%s', Value='%s'", MEMORY_FILE, key, value)
            return f"Okay, I've remembered that '{key}' is '{value}'"

        except IOError as e:
            logging.exception("IOError while saving memory to %s: %s", MEMORY_FILE, e)
            return "Sorry, I encountered an error trying to save that memory."
        except Exception as e:
            logging.exception("Unexpected error while saving memory to %s: %s", MEMORY_FILE, e)
            return "Sorry, an unexpected error occurred while saving the memory."

    loop = asyncio.get_running_loop()
    result_str = await loop.run_in_executor(None, save_sync)
    return result_str


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
                         logging.error("Memory storage %s is corrupted (not a dictionary). Cannot lookup.", MEMORY_FILE)
                         return "Memory storage is corrupted (not a dictionary). Cannot lookup."
                except json.JSONDecodeError:
                    logging.error("Memory storage %s is corrupted (invalid JSON). Cannot lookup.", MEMORY_FILE)
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
                return f"I couldn't find any memories in {MEMORY_FILE} where the key or value contained keywords from '{query}'."
            else:
                formatted_results = "\n".join(found_items)
                logging.info(
                    "Found %d memories in %s for query '%s'", len(found_items), MEMORY_FILE, query
                )
                return f"Here are the memories I found related to '{query}':\n{formatted_results}"
        except IOError as e:
            logging.exception("IOError while looking up memory from %s: %s", MEMORY_FILE, e)
            return "Sorry, I encountered an error trying to access memories."
        except Exception as e:
            logging.exception("Unexpected error while looking up memory from %s: %s", MEMORY_FILE, e)
            return "Sorry, an unexpected error occurred while looking up memories."

    loop = asyncio.get_running_loop()
    result_str = await loop.run_in_executor(None, lookup_sync)
    return result_str

def register_tools(mcp_instance: FastMCP):
    """Registers the memory tools with the MCP instance."""
    mcp_instance.tool()(add_memory)
    mcp_instance.tool()(lookup_memories)
    logging.info("Registered add_memory and lookup_memories tools.")
