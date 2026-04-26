# fastmcp-tools

Reusable MCP tool collection for [fastmcp-server](https://github.com/helmforgedev/fastmcp-server).

Each tool is a standalone Python file ready to deploy via inline ConfigMap, S3, or Git source.

## Tool Categories

| Category | Tools | Dependencies |
|----------|-------|-------------|
| **kubernetes** | `get_pods`, `get_logs`, `describe_resource` | `kubernetes` |
| **github** | read-only repo/issue/PR tools, controlled PR workflow tools, admin `run_gh` fallback | `requests` |
| **http** | `fetch_url`, `post_json` | `requests` |
| **database** | `query_postgres`, `query_mysql` | `psycopg2-binary`, `pymysql` |
| **notifications** | `send_slack`, `send_email` | `requests` (slack), stdlib (email) |

## Usage

### Pip Packages (auto-detected)

Install tool packages via `EXTRA_PIP_PACKAGES` — fastmcp-server automatically discovers and registers them:

```yaml
# values.yaml
extraPipPackages:
  - fastmcp-tools-kubernetes
  - fastmcp-tools-github
```

Available packages:

| Package | Pip name |
|---------|----------|
| Kubernetes | `fastmcp-tools-kubernetes` |
| GitHub | `fastmcp-tools-github` |
| HTTP | `fastmcp-tools-http` |
| Database | `fastmcp-tools-database` (extras: `[postgres]`, `[mysql]`, `[all]`) |
| Notifications | `fastmcp-tools-notifications` |

### Git Source

```yaml
# values.yaml
sources:
  git:
    enabled: true
    repository: 'https://github.com/helmforgedev/fastmcp-tools.git'
    branch: main
    path: tools/kubernetes
extraPipPackages:
  - kubernetes
```

### Inline (copy a single tool)

```yaml
sources:
  inline:
    tools:
      fetch_url.py: |
        # copy from tools/http/fetch_url.py
extraPipPackages:
  - requests
```

### S3 (upload tools directory)

```bash
aws s3 sync tools/ s3://my-bucket/mcp-tools/
```

## Environment Variables

Tools read credentials from environment variables when parameters are not provided:

| Variable | Used by |
|----------|---------|
| `GITHUB_TOKEN` | github tools |
| `DATABASE_URL` | query_postgres |
| `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` | query_mysql |
| `SLACK_WEBHOOK_URL` | send_slack |
| `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | send_email |

## GitHub Tools

The GitHub package favors typed REST API tools over raw shell access. Tools return structured dictionaries with `status`, concise data fields, and actionable error codes such as `missing_github_token`, `github_permission_denied`, `github_not_found`, and `reason_required`.

Read-only tools require `github:read`:

- `github_get_repo`
- `github_get_file`
- `github_list_issues`
- `github_get_issue`
- `github_list_pull_requests`
- `github_get_pull_request`
- `github_get_pr_checks`
- `github_get_workflow_run_logs`

Controlled write tools require a non-empty `reason` and support `dry_run`:

- `github_create_branch` (`github:write`)
- `github_commit_files` (`github:write`)
- `github_open_pull_request` (`github:pr`)
- `github_update_pull_request_body` (`github:pr`)
- `github_comment_pull_request` (`github:pr`)
- `github_add_labels` (`github:issue`)
- `github_request_review` (`github:pr`)

The legacy `run_gh(args)` tool is tagged as `admin` and requires `github:admin`. Keep it hidden from normal agent profiles with fastmcp-server visibility rules, for example `MCP_DISABLE_TAGS=admin`, and reserve it for debug or break-glass operations.

Legacy string-output wrappers (`create_pr`, `get_file`, and `list_issues`) remain importable for compatibility but declare `__mcp_auto_register__ = False`. MCP deployments should expose the structured `github_*` tools listed above.

Project-specific guardrails, such as owner allowlists or branch policies, should live in the private MCP content repository that consumes this package. For example, HelmForge keeps `github_open_guarded_pr` and repository policy checks outside this public reusable package.

### GitHub Environment

Set `GITHUB_TOKEN` only in the MCP server runtime that intentionally enables
GitHub tools. Do not put it in tool files, S3 content, knowledge docs, examples,
or client configuration.

Recommended token permissions:

| Tool group | Minimum token capability |
|------------|--------------------------|
| Read-only repo, issue, PR, checks, workflow logs | Repository read access |
| Branch creation and file commits | Contents write |
| Pull request creation and PR body updates | Pull requests write |
| Labels and issue comments | Issues write |
| `run_gh` | Break-glass only; depends on command |

Recommended server scopes:

| Server scope | Tools |
|--------------|-------|
| `github:read` | `github_get_repo`, `github_get_file`, `github_list_issues`, `github_get_issue`, `github_list_pull_requests`, `github_get_pull_request`, `github_get_pr_checks`, `github_get_workflow_run_logs` |
| `github:write` | `github_create_branch`, `github_commit_files` |
| `github:pr` | `github_open_pull_request`, `github_update_pull_request_body`, `github_comment_pull_request`, `github_request_review` |
| `github:issue` | `github_add_labels` |
| `github:admin` | `run_gh` |

### GitHub Examples

Dry-run a PR before creating it:

```python
github_open_pull_request(
    owner="helmforgedev",
    repo="charts",
    title="feat(charts): add fixture chart",
    head="feat/fixture-chart",
    base="main",
    body="Resolves #123",
    reason="Open chart contribution PR",
    dry_run=True,
)
```

Fetch PR checks:

```python
github_get_pr_checks(owner="helmforgedev", repo="charts", pr_number=123)
```

Commit files only after a project-specific policy layer has validated owner,
repo, branch, and paths:

```python
github_commit_files(
    owner="helmforgedev",
    repo="charts",
    branch="feat/fixture-chart",
    files=[{"path": "charts/fixture/README.md", "content": "Updated docs"}],
    message="docs(fixture): update chart docs",
    reason="Apply reviewed documentation update",
    dry_run=True,
)
```

## HTTP Tools

- `fetch_url`: fetch a URL with optional method and headers.
- `post_json`: POST a JSON payload.

Use these for trusted endpoints. Do not use them as a general SSRF-capable fetch
surface for arbitrary untrusted URLs in production agent workflows.

## Database Tools

- `query_postgres`
- `query_mysql`

Database tools read connection details from environment variables. Prefer
read-only database users, time-limited credentials, and network allowlists.

## Kubernetes Tools

- `get_pods`
- `get_logs`
- `describe_resource`

Run with a service account scoped to the namespaces and verbs the agent needs.

## Notification Tools

- `send_slack`
- `send_email`

Store webhook and SMTP credentials in the MCP server runtime secret store, not in
tool content.

## Tool Metadata

All tools use fastmcp-server magic variables:

- `__tags__` — categorization for visibility control
- `__timeout__` — execution timeout in seconds
- `__rate_limit__` — rate limiting (e.g., `"30/min"`)
- `__cache_ttl__` — result caching TTL in seconds
- `__max_output_size_kb__` — output truncation limit

## License

MIT
