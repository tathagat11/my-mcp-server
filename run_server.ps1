Write-Host "Activating virtual environment..."
# Note: You might need to set PowerShell's execution policy first if you haven't.
# Run PowerShell as Admin and execute: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# Or run with: powershell -ExecutionPolicy ByPass -File .\run_server.ps1
.\.venv\Scripts\Activate.ps1

Write-Host "Starting MCP server..."
uv run main.py

Write-Host "Server stopped. Press Enter to exit."
Read-Host -Prompt "Press Enter to exit"