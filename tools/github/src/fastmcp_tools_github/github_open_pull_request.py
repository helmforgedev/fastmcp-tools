"""Open a GitHub pull request."""

from fastmcp_tools_github.github_api import dry_run_result, github_request, require_reason

__tags__ = ["github", "write"]
__timeout__ = 30.0
__required_scopes__ = ["github:pr"]
__annotations_mcp__ = {
    "openWorldHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "title": "Open GitHub Pull Request",
}


def github_open_pull_request(
    owner: str,
    repo: str,
    title: str,
    head: str,
    base: str = "main",
    body: str = "",
    reason: str = "",
    dry_run: bool = False,
) -> dict:
    """Open a pull request, returning an existing open PR when one matches."""
    reason_error = require_reason(reason)
    if reason_error:
        return reason_error

    payload = {
        "title": title,
        "head": head,
        "base": base,
        "body": body,
        "reason": reason,
    }
    if dry_run:
        return dry_run_result("github_open_pull_request", payload)

    existing = github_request(
        "GET",
        f"/repos/{owner}/{repo}/pulls",
        params={"state": "open", "head": f"{owner}:{head}", "base": base},
    )
    if existing["status"] == "PASS" and existing["data"]:
        pr = existing["data"][0]
        return {
            "status": "PASS",
            "idempotent": True,
            "number": pr.get("number"),
            "html_url": pr.get("html_url"),
            "message": "Open pull request already exists for this head/base.",
        }

    result = github_request(
        "POST",
        f"/repos/{owner}/{repo}/pulls",
        json={"title": title, "head": head, "base": base, "body": body},
        expected=(201,),
    )
    if result["status"] != "PASS":
        return result
    pr = result["data"]
    return {
        "status": "PASS",
        "number": pr.get("number"),
        "html_url": pr.get("html_url"),
    }
