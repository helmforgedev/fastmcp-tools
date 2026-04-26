"""Get file contents from a GitHub repository.

Requires: requests
"""

__tags__ = ["github", "read"]
__timeout__ = 30.0
__cache_ttl__ = 120
__required_scopes__ = ["github:read"]
__mcp_auto_register__ = False
__annotations_mcp__ = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "title": "Get GitHub File",
}


def get_file(
    owner: str,
    repo: str,
    path: str,
    ref: str = "main",
) -> str:
    """Legacy wrapper; use github_get_file for MCP registration."""
    import base64
    import os

    import requests

    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
        headers=headers,
        params={"ref": ref},
        timeout=15,
    )
    resp.raise_for_status()

    data = resp.json()
    if data.get("type") != "file":
        return f"Error: {path} is a {data.get('type', 'unknown')}, not a file"

    content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    return content
