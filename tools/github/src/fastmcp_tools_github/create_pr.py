"""Create a GitHub pull request.

Requires: requests
"""

__tags__ = ["github", "write"]
__timeout__ = 30.0
__required_scopes__ = ["github:pr"]
__mcp_auto_register__ = False
__annotations_mcp__ = {
    "openWorldHint": True,
    "destructiveHint": False,
    "title": "Create GitHub Pull Request",
}


def create_pr(
    owner: str,
    repo: str,
    title: str,
    head: str,
    base: str = "main",
    body: str = "",
) -> str:
    """Legacy wrapper; use github_open_pull_request for MCP registration."""
    import os

    import requests

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return "Error: GITHUB_TOKEN environment variable required"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

    data = {"title": title, "head": head, "base": base, "body": body}

    resp = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/pulls",
        headers=headers,
        json=data,
        timeout=15,
    )
    resp.raise_for_status()

    pr = resp.json()
    return f"PR #{pr['number']} created: {pr['html_url']}"
