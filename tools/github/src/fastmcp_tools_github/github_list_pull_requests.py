"""List GitHub pull requests."""

from fastmcp_tools_github.github_api import github_request

__tags__ = ["github", "read"]
__timeout__ = 30.0
__cache_ttl__ = 60
__required_scopes__ = ["github:read"]
__annotations_mcp__ = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "title": "List GitHub Pull Requests",
}


def github_list_pull_requests(
    owner: str,
    repo: str,
    state: str = "open",
    base: str = "",
    head: str = "",
    limit: int = 20,
) -> dict:
    """List pull requests for a repository."""
    params = {"state": state, "per_page": min(max(limit, 1), 100)}
    if base:
        params["base"] = base
    if head:
        params["head"] = head
    result = github_request("GET", f"/repos/{owner}/{repo}/pulls", params=params)
    if result["status"] != "PASS":
        return result
    prs = result["data"][:limit]
    return {
        "status": "PASS",
        "pull_requests": [
            {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "state": pr.get("state"),
                "head": pr.get("head", {}).get("ref"),
                "base": pr.get("base", {}).get("ref"),
                "html_url": pr.get("html_url"),
            }
            for pr in prs
        ],
    }
