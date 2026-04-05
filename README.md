# fastmcp-tools

Reusable MCP tool collection for [fastmcp-server](https://github.com/helmforgedev/fastmcp-server).

Each tool is a standalone Python file ready to deploy via inline ConfigMap, S3, or Git source.

## Tool Categories

| Category | Tools | Dependencies |
|----------|-------|-------------|
| **kubernetes** | `get_pods`, `get_logs`, `describe_resource` | `kubernetes` |
| **github** | `list_issues`, `create_pr`, `get_file` | `requests` |
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

## Tool Metadata

All tools use fastmcp-server magic variables:

- `__tags__` — categorization for visibility control
- `__timeout__` — execution timeout in seconds
- `__rate_limit__` — rate limiting (e.g., `"30/min"`)
- `__cache_ttl__` — result caching TTL in seconds
- `__max_output_size_kb__` — output truncation limit

## License

MIT
