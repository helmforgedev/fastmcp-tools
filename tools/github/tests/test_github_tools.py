import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import fastmcp_tools_github.create_pr as legacy_create_pr
import fastmcp_tools_github.get_file as legacy_get_file
import fastmcp_tools_github.list_issues as legacy_list_issues
from fastmcp_tools_github import run_gh
from fastmcp_tools_github.github_create_branch import github_create_branch
from fastmcp_tools_github.github_get_file import github_get_file
from fastmcp_tools_github.github_get_repo import github_get_repo
from fastmcp_tools_github.github_get_workflow_run_logs import (
    github_get_workflow_run_logs,
)
from fastmcp_tools_github.github_list_issues import github_list_issues
from fastmcp_tools_github.github_open_pull_request import github_open_pull_request


class FakeResponse:
    def __init__(self, status_code=200, data=None, headers=None):
        self.status_code = status_code
        self._data = data
        self.headers = headers or {}
        self.text = "" if data is None else str(data)
        self.content = b"" if data is None else b"{}"

    def json(self):
        if isinstance(self._data, Exception):
            raise self._data
        return self._data


class GitHubToolTests(unittest.TestCase):
    def test_legacy_string_wrappers_are_not_auto_registered(self):
        self.assertFalse(legacy_create_pr.__mcp_auto_register__)
        self.assertFalse(legacy_get_file.__mcp_auto_register__)
        self.assertFalse(legacy_list_issues.__mcp_auto_register__)

    def test_run_gh_is_admin_debug_tool(self):
        self.assertIn("admin", run_gh.__tags__)
        self.assertIn("github:admin", run_gh.__required_scopes__)
        self.assertTrue(run_gh.__annotations_mcp__["destructiveHint"])

    def test_write_tool_requires_reason(self):
        result = github_create_branch("owner", "repo", "feature/example")

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["error_code"], "reason_required")

    def test_open_pull_request_supports_dry_run(self):
        result = github_open_pull_request(
            "owner",
            "repo",
            "Add feature",
            "feature/example",
            reason="tracking issue approved",
            dry_run=True,
        )

        self.assertEqual(result["status"], "DRY_RUN")
        self.assertEqual(result["action"], "github_open_pull_request")
        self.assertEqual(result["would_call"]["head"], "feature/example")

    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "token"}, clear=False)
    @mock.patch("fastmcp_tools_github.github_api.requests.request")
    def test_get_repo_returns_structured_metadata(self, request_mock):
        request_mock.return_value = FakeResponse(
            data={
                "full_name": "owner/repo",
                "private": False,
                "default_branch": "main",
                "html_url": "https://github.com/owner/repo",
                "description": "Example repo",
            }
        )

        result = github_get_repo("owner", "repo")

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["repo"]["full_name"], "owner/repo")
        request_mock.assert_called_once()

    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "token"}, clear=False)
    @mock.patch("fastmcp_tools_github.github_api.requests.request")
    def test_get_file_decodes_structured_content(self, request_mock):
        request_mock.return_value = FakeResponse(
            data={
                "type": "file",
                "sha": "abc123",
                "encoding": "base64",
                "content": "SGVsbG8=",
            }
        )

        result = github_get_file("owner", "repo", "README.md")

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["content"], "Hello")

    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "token"}, clear=False)
    @mock.patch("fastmcp_tools_github.github_api.requests.request")
    def test_list_issues_excludes_pull_requests(self, request_mock):
        request_mock.return_value = FakeResponse(
            data=[
                {
                    "number": 1,
                    "title": "Issue",
                    "state": "open",
                    "labels": [{"name": "bug"}],
                    "html_url": "https://github.com/owner/repo/issues/1",
                },
                {
                    "number": 2,
                    "title": "PR",
                    "pull_request": {},
                    "labels": [],
                },
            ]
        )

        result = github_list_issues("owner", "repo")

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["number"], 1)

    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "token"}, clear=False)
    @mock.patch("fastmcp_tools_github.github_api.requests.request")
    def test_open_pull_request_is_idempotent_for_existing_head(self, request_mock):
        request_mock.return_value = FakeResponse(
            data=[{"number": 42, "html_url": "https://github.com/owner/repo/pull/42"}]
        )

        result = github_open_pull_request(
            "owner",
            "repo",
            "Add feature",
            "feature/example",
            reason="tracking issue approved",
        )

        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["idempotent"])
        self.assertEqual(result["number"], 42)
        request_mock.assert_called_once()

    @mock.patch.dict(os.environ, {"GITHUB_TOKEN": "token"}, clear=False)
    @mock.patch("fastmcp_tools_github.github_api.requests.request")
    def test_workflow_logs_return_redirect_location_without_following(
        self, request_mock
    ):
        request_mock.return_value = FakeResponse(
            status_code=302,
            data=None,
            headers={"location": "https://example.com/logs.zip"},
        )

        result = github_get_workflow_run_logs("owner", "repo", 123)

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["download_url"], "https://example.com/logs.zip")
        self.assertFalse(request_mock.call_args.kwargs["allow_redirects"])


if __name__ == "__main__":
    unittest.main()
