"""Update a GitHub pull request body."""

from fastmcp_tools_github.github_api import dry_run_result, github_request, require_reason

__tags__ = ["github", "write"]
__timeout__ = 30.0
__required_scopes__ = ["github:pr"]
__annotations_mcp__ = {
    "openWorldHint": True,
    "destructiveHint": False,
    "title": "Update GitHub Pull Request Body",
}


def github_update_pull_request_body(
    owner: str,
    repo: str,
    pr_number: int,
    body: str,
    reason: str = "",
    dry_run: bool = False,
) -> dict:
    """Update the body of a pull request."""
    reason_error = require_reason(reason)
    if reason_error:
        return reason_error

    payload = {"body": body, "reason": reason}
    if dry_run:
        return dry_run_result("github_update_pull_request_body", payload)

    result = github_request(
        "PATCH", f"/repos/{owner}/{repo}/pulls/{pr_number}", json={"body": body}
    )
    if result["status"] != "PASS":
        return result
    return {"status": "PASS", "number": result["data"].get("number")}
