"""Shared GitHub API helpers for fastmcp-tools-github."""

from __future__ import annotations

import base64
import os
from typing import Any

import requests

__mcp_auto_register__ = False


def github_request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: Any | None = None,
    expected: tuple[int, ...] = (200,),
    timeout: int = 20,
    allow_redirects: bool = True,
) -> dict:
    """Call the GitHub REST API and return a structured result."""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return {
            "status": "ERROR",
            "error_code": "missing_github_token",
            "message": "GITHUB_TOKEN environment variable is required.",
        }

    api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        response = requests.request(
            method,
            f"{api_url}/{path.lstrip('/')}",
            headers=headers,
            params=params,
            json=json,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )
    except requests.RequestException as exc:
        return {
            "status": "ERROR",
            "error_code": "github_request_failed",
            "message": str(exc),
        }

    data = _decode_json(response)
    if response.status_code not in expected:
        return {
            "status": "ERROR",
            "error_code": _error_code(response.status_code),
            "message": _error_message(response, data),
            "http_status": response.status_code,
            "data": data,
        }

    return {
        "status": "PASS",
        "http_status": response.status_code,
        "data": data,
        "headers": {
            "x-ratelimit-remaining": response.headers.get("x-ratelimit-remaining"),
            "x-ratelimit-reset": response.headers.get("x-ratelimit-reset"),
            "location": response.headers.get("location"),
        },
    }


def require_reason(reason: str) -> dict | None:
    """Return an error result when a write operation has no reason."""
    if reason and reason.strip():
        return None
    return {
        "status": "ERROR",
        "error_code": "reason_required",
        "message": "Write operations require a non-empty reason.",
    }


def dry_run_result(action: str, payload: dict) -> dict:
    """Return a consistent dry-run response."""
    return {
        "status": "DRY_RUN",
        "action": action,
        "would_call": payload,
    }


def encode_content(content: str) -> str:
    """Base64 encode file content for the GitHub Contents API."""
    return base64.b64encode(content.encode("utf-8")).decode("ascii")


def _decode_json(response) -> Any:
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return response.text


def _error_code(status_code: int) -> str:
    if status_code in {401, 403}:
        return "github_permission_denied"
    if status_code == 404:
        return "github_not_found"
    if status_code == 409:
        return "github_conflict"
    if status_code == 422:
        return "github_validation_failed"
    if status_code == 429:
        return "github_rate_limited"
    return "github_api_error"


def _error_message(response, data: Any) -> str:
    if isinstance(data, dict) and data.get("message"):
        return str(data["message"])
    return f"GitHub API returned HTTP {response.status_code}."
