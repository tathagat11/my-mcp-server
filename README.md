# My MCP Server

A simple Model Context Protocol (MCP) server implemented in Python using `FastMCP`.

This server provides the following capabilities to an MCP client (like Claude):
*   **Google Search:** Allows the client to perform Google searches via the Custom Search API.
*   **Memory Store:** Allows the client to store and retrieve simple key-value memories persisted in a local JSON file (`data/memories.json`).

## Prerequisites

*   Python 3.11+
*   [uv](https://github.com/astral-sh/uv) (Python package installer and virtual environment manager)
*   Google API Key and Custom Search Engine (CSE) ID for the Google Search tool.

## Setup

1.  **Install `uv`:**
    *   **PowerShell (Windows):**
        ```powershell
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        ```
    *   **Shell (macOS, Linux):**
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```

2.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd my-mcp
    ```

3.  **Create and Activate Virtual Environment:**
    ```bash
    uv venv
    # Activate the environment:
    # Windows (CMD): .venv\Scripts\activate.bat
    # Windows (PowerShell): .venv\Scripts\Activate.ps1
    # macOS/Linux (Bash/Zsh): source .venv/bin/activate
    ```

4.  **Install Dependencies:**
    ```bash
    uv pip sync pyproject.toml
    ```
    (This installs dependencies specified in your `pyproject.toml`)

5.  **Configure Environment Variables:**
    *   Create a file named `.env` in the root directory (`my-mcp`).
    *   Add your Google API credentials to the `.env` file:
        ```env
        GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
        GOOGLE_CSE_ID="YOUR_GOOGLE_CSE_ID_HERE"
        ```
    *   Replace the placeholder values with your actual key and ID. You can obtain these from the [Google Cloud Console](https://console.cloud.google.com/) (API Key, enable Custom Search API) and the [Programmable Search Engine control panel](https://programmablesearchengine.google.com/controlpanel/all) (Search engine ID).

## Running the Server

Ensure your virtual environment is activated. Then, run the main script:

```bash
uv run main.py
```

The server will start and listen for connections from an MCP client using standard input/output (`stdio`). The server logs messages, including warnings about missing API keys or tool registration status, to standard error.