
import os
import pathlib
import socket
import subprocess
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("smart-terminal")

# Restrict everything to current project root
PROJECT_ROOT = pathlib.Path.cwd().resolve()


# -----------------------------
# Helper: Safe Path Validation
# -----------------------------
def safe_path(path: str) -> pathlib.Path:
    full_path = (PROJECT_ROOT / path).resolve()
    if not str(full_path).startswith(str(PROJECT_ROOT)):
        raise ValueError("Access outside project directory is not allowed.")
    return full_path


# -----------------------------
# Tool 1: Current Directory
# -----------------------------
@mcp.tool()
def current_working_directory() -> str:
    return str(PROJECT_ROOT)


# -----------------------------
# Tool 2: List Directory
# -----------------------------
@mcp.tool()
def list_directory(path: str = ".") -> list:
    directory = safe_path(path)
    if not directory.exists() or not directory.is_dir():
        return ["Invalid directory"]

    return [item.name for item in directory.iterdir()]


# -----------------------------
# Tool 3: Read File
# -----------------------------
@mcp.tool()
def read_file(path: str) -> str:
    file_path = safe_path(path)

    if not file_path.exists() or not file_path.is_file():
        return "File not found"

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# -----------------------------
# Tool 4: Search File by Name
# -----------------------------
@mcp.tool()
def search_file(filename: str) -> list:
    matches = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for file in files:
            if filename.lower() in file.lower():
                matches.append(str(pathlib.Path(root) / file))
    return matches if matches else ["No matching files found"]


# -----------------------------
# Tool 5: File Info
# -----------------------------
@mcp.tool()
def file_info(path: str) -> dict:
    file_path = safe_path(path)

    if not file_path.exists():
        return {"error": "File not found"}

    stat = file_path.stat()

    return {
        "name": file_path.name,
        "size_kb": round(stat.st_size / 1024, 2),
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "is_directory": file_path.is_dir()
    }


# -----------------------------
# Tool 6: Check Port
# -----------------------------
@mcp.tool()
def check_port(port: int) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(("127.0.0.1", port))
        if result == 0:
            return f"Port {port} is OPEN"
        else:
            return f"Port {port} is FREE"


# -----------------------------
# Tool 7: Who is Using Port (Windows)
# -----------------------------
@mcp.tool()
def who_is_using_port(port: int) -> str:
    try:
        result = subprocess.check_output(
            f"netstat -ano | findstr :{port}",
            shell=True,
            text=True
        )
        return result if result else "No process found using this port"
    except subprocess.CalledProcessError:
        return "No process found using this port"


# -----------------------------
# Start Server (STDIO)
# -----------------------------
if __name__ == "__main__":
    mcp.run()