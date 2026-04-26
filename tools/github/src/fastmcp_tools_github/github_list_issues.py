"""List GitHub issues with structured output."""

from fastmcp_tools_github.github_api import github_request

__tags__ = ["github", "read"]
__timeout__ = 30.0
__cache_ttl__ = 60
__required_scopes__ = ["github:read"]
__annotations_mcp__ = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "title": "List GitHub Issues",
}


def github_list_issues(
    owner: str,
    repo: str,
    state: str = "open",
    labels: str = "",
    limit: int = 20,
) -> dict:
    """List issues for a repository, excluding pull requests."""
    params = {"state": state, "per_page": min(max(limit, 1), 100)}
    if labels:
        params["labels"] = labels

    result = github_request("GET", f"/repos/{owner}/{repo}/issues", params=params)
    if result["status"] != "PASS":
        return result

    issues = [issue for issue in result["data"] if "pull_request" not in issue][:limit]
    return {
        "status": "PASS",
        "issues": [
            {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "labels": [label.get("name") for label in issue.get("labels", [])],
                "html_url": issue.get("html_url"),
            }
            for issue in issues
        ],
    }
