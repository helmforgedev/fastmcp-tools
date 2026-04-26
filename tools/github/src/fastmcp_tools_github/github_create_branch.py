"""Create a GitHub branch."""

from fastmcp_tools_github.github_api import dry_run_result, github_request, require_reason

__tags__ = ["github", "write"]
__timeout__ = 30.0
__required_scopes__ = ["github:write"]
__annotations_mcp__ = {
    "openWorldHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "title": "Create GitHub Branch",
}


def github_create_branch(
    owner: str,
    repo: str,
    branch: str,
    source_branch: str = "main",
    reason: str = "",
    dry_run: bool = False,
) -> dict:
    """Create a branch from an existing source branch."""
    reason_error = require_reason(reason)
    if reason_error:
        return reason_error

    payload = {
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "source_branch": source_branch,
        "reason": reason,
    }
    if dry_run:
        return dry_run_result("github_create_branch", payload)

    source = github_request(
        "GET", f"/repos/{owner}/{repo}/git/ref/heads/{source_branch}"
    )
    if source["status"] != "PASS":
        return source

    sha = source["data"].get("object", {}).get("sha")
    create = github_request(
        "POST",
        f"/repos/{owner}/{repo}/git/refs",
        json={"ref": f"refs/heads/{branch}", "sha": sha},
        expected=(201,),
    )
    if create["status"] != "PASS" and create.get("http_status") == 422:
        return {
            "status": "PASS",
            "idempotent": True,
            "message": f"Branch '{branch}' already exists or cannot be created.",
            "data": create.get("data"),
        }
    if create["status"] != "PASS":
        return create
    return {"status": "PASS", "branch": branch, "ref": create["data"].get("ref")}
