"""Request reviewers on a GitHub pull request."""

from fastmcp_tools_github.github_api import dry_run_result, github_request, require_reason

__tags__ = ["github", "write"]
__timeout__ = 30.0
__required_scopes__ = ["github:pr"]
__annotations_mcp__ = {
    "openWorldHint": True,
    "destructiveHint": False,
    "title": "Request GitHub Review",
}


def github_request_review(
    owner: str,
    repo: str,
    pr_number: int,
    reviewers: list[str] | None = None,
    team_reviewers: list[str] | None = None,
    reason: str = "",
    dry_run: bool = False,
) -> dict:
    """Request users or teams to review a pull request."""
    reason_error = require_reason(reason)
    if reason_error:
        return reason_error
    payload = {
        "reviewers": reviewers or [],
        "team_reviewers": team_reviewers or [],
        "reason": reason,
    }
    if dry_run:
        return dry_run_result("github_request_review", payload)

    result = github_request(
        "POST",
        f"/repos/{owner}/{repo}/pulls/{pr_number}/requested_reviewers",
        json={
            "reviewers": reviewers or [],
            "team_reviewers": team_reviewers or [],
        },
        expected=(201,),
    )
    if result["status"] != "PASS":
        return result
    return {"status": "PASS", "number": result["data"].get("number")}
