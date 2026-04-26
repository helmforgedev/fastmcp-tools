"""Get a GitHub pull request."""

from fastmcp_tools_github.github_api import github_request

__tags__ = ["github", "read"]
__timeout__ = 30.0
__cache_ttl__ = 60
__required_scopes__ = ["github:read"]
__annotations_mcp__ = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "title": "Get GitHub Pull Request",
}


def github_get_pull_request(owner: str, repo: str, pr_number: int) -> dict:
    """Get a pull request by number."""
    result = github_request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")
    if result["status"] != "PASS":
        return result
    pr = result["data"]
    return {
        "status": "PASS",
        "pull_request": {
            "number": pr.get("number"),
            "title": pr.get("title"),
            "state": pr.get("state"),
            "merged": pr.get("merged"),
            "head": pr.get("head", {}).get("ref"),
            "base": pr.get("base", {}).get("ref"),
            "html_url": pr.get("html_url"),
            "body": pr.get("body"),
        },
    }
