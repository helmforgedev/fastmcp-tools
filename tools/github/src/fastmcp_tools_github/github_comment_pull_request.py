"""Comment on a GitHub pull request."""

from fastmcp_tools_github.github_api import dry_run_result, github_request, require_reason

__tags__ = ["github", "write"]
__timeout__ = 30.0
__required_scopes__ = ["github:pr"]
__annotations_mcp__ = {
    "openWorldHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "title": "Comment on GitHub Pull Request",
}


def github_comment_pull_request(
    owner: str,
    repo: str,
    pr_number: int,
    body: str,
    reason: str = "",
    dry_run: bool = False,
) -> dict:
    """Add a comment to a pull request, avoiding duplicate exact comments."""
    reason_error = require_reason(reason)
    if reason_error:
        return reason_error

    payload = {"body": body, "reason": reason}
    if dry_run:
        return dry_run_result("github_comment_pull_request", payload)

    comments = github_request(
        "GET", f"/repos/{owner}/{repo}/issues/{pr_number}/comments"
    )
    if comments["status"] == "PASS":
        for comment in comments["data"]:
            if comment.get("body") == body:
                return {
                    "status": "PASS",
                    "idempotent": True,
                    "comment_id": comment.get("id"),
                    "html_url": comment.get("html_url"),
                    "message": "An identical comment already exists.",
                }

    result = github_request(
        "POST",
        f"/repos/{owner}/{repo}/issues/{pr_number}/comments",
        json={"body": body},
        expected=(201,),
    )
    if result["status"] != "PASS":
        return result
    return {
        "status": "PASS",
        "comment_id": result["data"].get("id"),
        "html_url": result["data"].get("html_url"),
    }
