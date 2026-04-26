"""Get GitHub repository file content."""

from __future__ import annotations

import base64

from fastmcp_tools_github.github_api import github_request

__tags__ = ["github", "read"]
__timeout__ = 30.0
__cache_ttl__ = 120
__required_scopes__ = ["github:read"]
__annotations_mcp__ = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "title": "Get GitHub File",
}


def github_get_file(owner: str, repo: str, path: str, ref: str = "main") -> dict:
    """Get a text file from a GitHub repository using the Contents API."""
    result = github_request(
        "GET",
        f"/repos/{owner}/{repo}/contents/{path}",
        params={"ref": ref},
    )
    if result["status"] != "PASS":
        return result

    data = result["data"]
    if data.get("type") != "file":
        return {
            "status": "ERROR",
            "error_code": "not_a_file",
            "message": f"{path} is a {data.get('type', 'unknown')}, not a file.",
        }

    try:
        content = base64.b64decode(data.get("content", "")).decode(
            "utf-8", errors="replace"
        )
    except ValueError as exc:
        return {
            "status": "ERROR",
            "error_code": "invalid_file_encoding",
            "message": str(exc),
        }

    return {
        "status": "PASS",
        "path": path,
        "ref": ref,
        "sha": data.get("sha"),
        "encoding": data.get("encoding"),
        "content": content,
    }
