"""Get GitHub pull request checks."""

from fastmcp_tools_github.github_api import github_request

__tags__ = ["github", "read"]
__timeout__ = 30.0
__cache_ttl__ = 30
__required_scopes__ = ["github:read"]
__annotations_mcp__ = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "title": "Get GitHub PR Checks",
}


def github_get_pr_checks(owner: str, repo: str, pr_number: int) -> dict:
    """Get check runs for the pull request head commit."""
    pr_result = github_request("GET", f"/repos/{owner}/{repo}/pulls/{pr_number}")
    if pr_result["status"] != "PASS":
        return pr_result

    sha = pr_result["data"].get("head", {}).get("sha")
    if not sha:
        return {
            "status": "ERROR",
            "error_code": "missing_head_sha",
            "message": "Pull request response did not include head sha.",
        }

    checks_result = github_request(
        "GET", f"/repos/{owner}/{repo}/commits/{sha}/check-runs"
    )
    if checks_result["status"] != "PASS":
        return checks_result

    runs = checks_result["data"].get("check_runs", [])
    return {
        "status": "PASS",
        "head_sha": sha,
        "checks": [
            {
                "name": run.get("name"),
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
                "html_url": run.get("html_url"),
            }
            for run in runs
        ],
    }
