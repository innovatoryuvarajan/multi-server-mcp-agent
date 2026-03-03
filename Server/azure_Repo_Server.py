import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from fastmcp import FastMCP

load_dotenv()

AZURE_ORG = os.getenv("AZURE_ORG")
AZURE_PROJECT = os.getenv("AZURE_PROJECT")
AZURE_PAT = os.getenv("AZURE_PAT")

if not AZURE_ORG or not AZURE_PROJECT or not AZURE_PAT:
    raise ValueError("Missing Azure DevOps configuration in .env")

BASE_URL = f"https://dev.azure.com/{AZURE_ORG}"
API_VERSION = "7.0"

mcp = FastMCP("Azure-Repos-Server")


# ---------------------------------
# 🔹 Common Azure Request Handler
# ---------------------------------
def azure_request(method: str, url: str, **kwargs):
    try:
        response = requests.request(
            method,
            url,
            auth=HTTPBasicAuth("", AZURE_PAT),
            timeout=15,
            **kwargs
        )

        if response.status_code == 404:
            return {"error": "Resource not found", "status_code": 404}

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# ---------------------------------
# 🔹 List Repositories
# ---------------------------------
@mcp.tool
def list_repositories():
    """List all repositories in the project."""

    url = f"{BASE_URL}/{AZURE_PROJECT}/_apis/git/repositories?api-version={API_VERSION}"

    data = azure_request("GET", url)

    if "error" in data:
        return data

    repos = [
        {
            "id": repo["id"],
            "name": repo["name"],
            "defaultBranch": repo.get("defaultBranch")
        }
        for repo in data.get("value", [])
    ]

    return {
        "count": len(repos),
        "repositories": repos
    }


# ---------------------------------
# 🔹 List Branches
# ---------------------------------
@mcp.tool
def list_branches(repository: str):
    """List branches of a repository."""

    url = f"{BASE_URL}/{AZURE_PROJECT}/_apis/git/repositories/{repository}/refs?filter=heads/&api-version={API_VERSION}"

    data = azure_request("GET", url)

    if "error" in data:
        return data

    branches = [
        ref["name"].replace("refs/heads/", "")
        for ref in data.get("value", [])
    ]

    return {
        "count": len(branches),
        "branches": branches
    }


# ---------------------------------
# 🔹 Get Latest Commits
# ---------------------------------
@mcp.tool
def get_latest_commits(repository: str, branch: str = "main", top: int = 5):
    """Get latest commits from a branch."""

    url = (
        f"{BASE_URL}/{AZURE_PROJECT}/_apis/git/repositories/"
        f"{repository}/commits?searchCriteria.itemVersion.version={branch}"
        f"&$top={top}&api-version={API_VERSION}"
    )

    data = azure_request("GET", url)

    if "error" in data:
        return data

    commits = [
        {
            "commitId": c["commitId"],
            "author": c["author"]["name"],
            "comment": c["comment"],
            "date": c["author"]["date"]
        }
        for c in data.get("value", [])
    ]

    return {
        "count": len(commits),
        "commits": commits
    }


# ---------------------------------
# 🔹 List Active Pull Requests
# ---------------------------------
@mcp.tool
def list_pull_requests(repository: str):
    """List active pull requests."""

    url = (
        f"{BASE_URL}/{AZURE_PROJECT}/_apis/git/repositories/"
        f"{repository}/pullrequests?searchCriteria.status=active"
        f"&api-version={API_VERSION}"
    )

    data = azure_request("GET", url)

    if "error" in data:
        return data

    prs = [
        {
            "id": pr["pullRequestId"],
            "title": pr["title"],
            "createdBy": pr["createdBy"]["displayName"],
            "status": pr["status"]
        }
        for pr in data.get("value", [])
    ]

    return {
        "count": len(prs),
        "pull_requests": prs
    }


# ---------------------------------
# 🔹 Browse Repo Files
# ---------------------------------
@mcp.tool
def get_repo_items(repository: str, path: str = "/"):
    """Browse repository files/folders."""

    url = (
        f"{BASE_URL}/{AZURE_PROJECT}/_apis/git/repositories/"
        f"{repository}/items?scopePath={path}"
        f"&recursionLevel=OneLevel&api-version={API_VERSION}"
    )

    data = azure_request("GET", url)

    if "error" in data:
        return data

    items = [
        {
            "path": item["path"],
            "isFolder": item["isFolder"]
        }
        for item in data.get("value", [])
    ]

    return {
        "count": len(items),
        "items": items
    }


# ---------------------------------
# 🔹 Run MCP Server
# ---------------------------------
if __name__ == "__main__":
    mcp.run(transport="http", port=8002)