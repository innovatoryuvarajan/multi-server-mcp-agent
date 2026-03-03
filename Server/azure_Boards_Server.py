
import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from fastmcp import FastMCP

load_dotenv()

AZURE_ORG = os.getenv("AZURE_ORG")
AZURE_PROJECT = os.getenv("AZURE_PROJECT")
AZURE_PAT = os.getenv("AZURE_PAT")

if not AZURE_ORG or not AZURE_PAT:
    raise ValueError("Missing Azure DevOps configuration in .env")

BASE_URL = f"https://dev.azure.com/{AZURE_ORG}"
API_VERSION = "7.0"

mcp = FastMCP("Azure-DevOps-Server")


# -----------------------------
# 🔹 Utility: Safe Azure Request
# -----------------------------
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


# -----------------------------
# 🔹 Utility: Fetch Work Item Details
# -----------------------------
def fetch_work_item_details(project: str, ids: list):
    if not ids:
        return []

    ids_string = ",".join(str(i) for i in ids)

    url = (
        f"{BASE_URL}/{project}/_apis/wit/workitems"
        f"?ids={ids_string}&api-version={API_VERSION}"
    )

    data = azure_request("GET", url)

    if "error" in data:
        return data

    results = []
    for item in data.get("value", []):
        fields = item.get("fields", {})
        results.append({
            "id": item.get("id"),
            "title": fields.get("System.Title"),
            "state": fields.get("System.State"),
            "assignedTo": (
                fields.get("System.AssignedTo", {}).get("displayName")
                if isinstance(fields.get("System.AssignedTo"), dict)
                else fields.get("System.AssignedTo")
            ),
            "type": fields.get("System.WorkItemType")
        })

    return results


# -----------------------------
# 🔹 Tool: List Projects
# -----------------------------
@mcp.tool
def list_projects():
    """List all Azure DevOps projects."""
    url = f"{BASE_URL}/_apis/projects?api-version={API_VERSION}"

    data = azure_request("GET", url)

    if "error" in data:
        return data

    projects = [p["name"] for p in data.get("value", [])]

    return {
        "count": len(projects),
        "projects": projects
    }


# -----------------------------
# 🔹 Tool: Generic WIQL Query
# -----------------------------
@mcp.tool
def query_work_items(project: str, wiql: str):
    """Run custom WIQL query on a project."""

    wiql_url = f"{BASE_URL}/{project}/_apis/wit/wiql?api-version={API_VERSION}"

    data = azure_request(
        "POST",
        wiql_url,
        json={"query": wiql},
        headers={"Content-Type": "application/json"},
    )

    if "error" in data:
        return data

    work_items = data.get("workItems", [])
    ids = [item["id"] for item in work_items]

    detailed_items = fetch_work_item_details(project, ids)

    return {
        "count": len(detailed_items),
        "items": detailed_items
    }


# -----------------------------
# 🔹 Tool: Active Work Items
# -----------------------------
@mcp.tool
def get_active_work_items(project: str):
    """Fetch active work items."""

    wiql = """
        SELECT [System.Id]
        FROM WorkItems
        WHERE [System.State] = 'Active'
        ORDER BY [System.ChangedDate] DESC
    """

    return query_work_items(project, wiql)


# -----------------------------
# 🔹 Tool: Unassigned Work Items
# -----------------------------
@mcp.tool
def get_unassigned_work_items(project: str):
    """Fetch unassigned active work items."""

    wiql = """
        SELECT [System.Id]
        FROM WorkItems
        WHERE
            [System.State] = 'Active'
            AND [System.AssignedTo] = ''
    """

    return query_work_items(project, wiql)


# -----------------------------
# 🔹 Tool: Current Epics
# -----------------------------
@mcp.tool
def get_current_epics(project: str):
    """Fetch active epics."""

    wiql = """
        SELECT [System.Id]
        FROM WorkItems
        WHERE
            [System.WorkItemType] = 'Epic'
            AND [System.State] <> 'Closed'
    """

    return query_work_items(project, wiql)

@mcp.tool
def get_work_item_comments(project: str, work_item_id: int):
    """Fetch discussion/comments for a work item."""

    url = (
        f"{BASE_URL}/{project}/_apis/wit/workItems/"
        f"{work_item_id}/comments?api-version=7.0-preview.3"
    )

    data = azure_request("GET", url)

    if "error" in data:
        return data

    comments = data.get("comments", [])

    if not comments:
        return {
            "count": 0,
            "comments": []
        }

    results = []
    for comment in comments:
        results.append({
            "commentId": comment.get("id"),
            "text": comment.get("text"),
            "createdBy": comment.get("createdBy", {}).get("displayName"),
            "createdDate": comment.get("createdDate")
        })

    return {
        "count": len(results),
        "comments": results
    }

@mcp.tool
def get_pipeline_status(project: str):
    """Fetch latest pipeline run status for the project."""

    url = f"{BASE_URL}/{project}/_apis/build/builds?api-version={API_VERSION}&$top=5"

    data = azure_request("GET", url)

    if "error" in data:
        return data

    builds = data.get("value", [])

    if not builds:
        return {
            "count": 0,
            "message": "No pipelines found."
        }

    results = []
    for build in builds:
        results.append({
            "id": build.get("id"),
            "definitionName": build.get("definition", {}).get("name"),
            "status": build.get("status"),
            "result": build.get("result"),
            "queueTime": build.get("queueTime")
        })

    return {
        "count": len(results),
        "pipelines": results
    }
# -----------------------------
# 🔹 Run MCP Server
# -----------------------------
if __name__ == "__main__":
    mcp.run(transport="http", port=8001)