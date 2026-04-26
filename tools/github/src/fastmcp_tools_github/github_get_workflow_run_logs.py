"""Get GitHub Actions workflow run logs link."""

from fastmcp_tools_github.github_api import github_request

__tags__ = ["github", "read"]
__timeout__ = 30.0
__required_scopes__ = ["github:read"]
__annotations_mcp__ = {
    "readOnlyHint": True,
    "openWorldHint": True,
    "title": "Get GitHub Workflow Run Logs",
}


def github_get_workflow_run_logs(owner: str, repo: str, run_id: int) -> dict:
    """Get a short-lived workflow run logs download URL."""
    result = github_request(
        "GET",
        f"/repos/{owner}/{repo}/actions/runs/{run_id}/logs",
        expected=(302,),
        allow_redirects=False,
    )
    if result["status"] != "PASS":
        return result
    return {
        "status": "PASS",
        "run_id": run_id,
        "download_url": result.get("headers", {}).get("location"),
        "message": "GitHub returns a short-lived redirect URL for workflow logs.",
    }
