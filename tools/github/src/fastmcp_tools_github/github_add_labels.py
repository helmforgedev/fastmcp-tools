"""Add labels to a GitHub issue or pull request."""

from fastmcp_tools_github.github_api import dry_run_result, github_request, require_reason

__tags__ = ["github", "write"]
__timeout__ = 30.0
__required_scopes__ = ["github:issue"]
__annotations_mcp__ = {
    "openWorldHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "title": "Add GitHub Labels",
}


def github_add_labels(
    owner: str,
    repo: str,
    issue_number: int,
    labels: list[str],
    reason: str = "",
    dry_run: bool = False,
) -> dict:
    """Add labels to an issue or pull request."""
    reason_error = require_reason(reason)
    if reason_error:
        return reason_error
    clean_labels = [label.strip() for label in labels if label.strip()]
    payload = {"labels": clean_labels, "reason": reason}
    if dry_run:
        return dry_run_result("github_add_labels", payload)
    if not clean_labels:
        return {"status": "ERROR", "error_code": "labels_required", "message": "labels is empty."}

    result = github_request(
        "POST",
        f"/repos/{owner}/{repo}/issues/{issue_number}/labels",
        json={"labels": clean_labels},
    )
    if result["status"] != "PASS":
        return result
    return {"status": "PASS", "labels": [label.get("name") for label in result["data"]]}
