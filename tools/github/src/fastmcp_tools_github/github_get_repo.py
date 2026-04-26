"""Get GitHub repository metadata."""

from fastmcp_tools_github.github_api import github_request

__tags__ = ["github", "read"]
__timeout__ = 30.0
__cache_ttl__ = 60
__required_scopes__ = ["github:read"]
__annotations_mcp__ = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "title": "Get GitHub Repository",
}


def github_get_repo(owner: str, repo: str) -> dict:
    """Get metadata for a GitHub repository."""
    result = github_request("GET", f"/repos/{owner}/{repo}")
    if result["status"] != "PASS":
        return result
    data = result["data"]
    return {
        "status": "PASS",
        "repo": {
            "full_name": data.get("full_name"),
            "private": data.get("private"),
            "default_branch": data.get("default_branch"),
            "html_url": data.get("html_url"),
            "description": data.get("description"),
        },
    }
