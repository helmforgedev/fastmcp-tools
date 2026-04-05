"""Get file contents from a GitHub repository.

Requires: requests
"""

__tags__ = ["github", "read"]
__timeout__ = 30.0
__cache_ttl__ = 120


def get_file(
    owner: str,
    repo: str,
    path: str,
    ref: str = "main",
) -> str:
    """Get file contents from a GitHub repository."""
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
