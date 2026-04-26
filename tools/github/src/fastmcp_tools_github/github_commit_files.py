"""Commit files to a GitHub branch using the Contents API."""

from fastmcp_tools_github.github_api import (
    dry_run_result,
    encode_content,
    github_request,
    require_reason,
)

__tags__ = ["github", "write"]
__timeout__ = 60.0
__required_scopes__ = ["github:write"]
__annotations_mcp__ = {
    "openWorldHint": True,
    "destructiveHint": False,
    "title": "Commit GitHub Files",
}


def github_commit_files(
    owner: str,
    repo: str,
    branch: str,
    files: list[dict],
    message: str,
    reason: str = "",
    dry_run: bool = False,
) -> dict:
    """Commit one or more text files to a branch.

    files items must contain `path` and `content`.
    """
    reason_error = require_reason(reason)
    if reason_error:
        return reason_error
    if not files:
        return {"status": "ERROR", "error_code": "files_required", "message": "files is empty."}

    payload = {
        "branch": branch,
        "message": message,
        "files": [{"path": item.get("path")} for item in files],
        "reason": reason,
    }
    if dry_run:
        return dry_run_result("github_commit_files", payload)

    committed = []
    for item in files:
        path = item.get("path", "")
        content = item.get("content", "")
        if not path:
            return {"status": "ERROR", "error_code": "path_required", "message": "Every file needs path."}

        existing = github_request(
            "GET",
            f"/repos/{owner}/{repo}/contents/{path}",
            params={"ref": branch},
            expected=(200, 404),
        )
        sha = None
        if existing["status"] == "PASS" and isinstance(existing.get("data"), dict):
            sha = existing["data"].get("sha")

        body = {
            "message": message,
            "content": encode_content(content),
            "branch": branch,
        }
        if sha:
            body["sha"] = sha

        result = github_request(
            "PUT",
            f"/repos/{owner}/{repo}/contents/{path}",
            json=body,
            expected=(200, 201),
            timeout=30,
        )
        if result["status"] != "PASS":
            return result
        committed.append(
            {
                "path": path,
                "sha": result["data"].get("content", {}).get("sha"),
                "html_url": result["data"].get("content", {}).get("html_url"),
            }
        )

    return {"status": "PASS", "committed": committed}
