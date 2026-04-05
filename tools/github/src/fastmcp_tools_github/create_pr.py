"""Create a GitHub pull request.

Requires: requests
"""

__tags__ = ["github", "write"]
__timeout__ = 30.0


def create_pr(
    owner: str,
    repo: str,
    title: str,
    head: str,
    base: str = "main",
    body: str = "",
) -> str:
    """Create a pull request on a GitHub repository."""
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
