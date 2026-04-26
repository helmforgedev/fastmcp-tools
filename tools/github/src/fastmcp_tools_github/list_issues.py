"""List GitHub issues for a repository.

Requires: requests
"""

__tags__ = ["github", "read"]
__timeout__ = 30.0
__cache_ttl__ = 60
__required_scopes__ = ["github:read"]
__mcp_auto_register__ = False
__annotations_mcp__ = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "title": "List GitHub Issues",
}


def list_issues(
    owner: str,
    repo: str,
    state: str = "open",
    labels: str = "",
    limit: int = 20,
) -> str:
    """Legacy wrapper; use github_list_issues for MCP registration."""
    import os

    import requests

    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    params = {"state": state, "per_page": min(limit, 100)}
    if labels:
        params["labels"] = labels

    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        headers=headers,
        params=params,
        timeout=15,
    )
    resp.raise_for_status()

    issues = resp.json()
    lines = [f"Issues for {owner}/{repo} ({state}):"]
    for issue in issues[:limit]:
        labels_str = ", ".join(lbl["name"] for lbl in issue.get("labels", []))
        lines.append(f"  #{issue['number']} {issue['title']} [{labels_str}]")

    if len(lines) == 1:
        lines.append("  (no issues found)")

    return "\n".join(lines)
