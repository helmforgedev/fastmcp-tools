"""Get a GitHub issue."""

from fastmcp_tools_github.github_api import github_request

__tags__ = ["github", "read"]
__timeout__ = 30.0
__cache_ttl__ = 60
__required_scopes__ = ["github:read"]
__annotations_mcp__ = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "title": "Get GitHub Issue",
}


def github_get_issue(owner: str, repo: str, issue_number: int) -> dict:
    """Get a single GitHub issue by number."""
    result = github_request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")
    if result["status"] != "PASS":
        return result
    issue = result["data"]
    return {
        "status": "PASS",
        "issue": {
            "number": issue.get("number"),
            "title": issue.get("title"),
            "state": issue.get("state"),
            "html_url": issue.get("html_url"),
            "labels": [label.get("name") for label in issue.get("labels", [])],
        },
    }
