"""Fetch content from a URL.

Requires: requests
"""

__tags__ = ["http", "read"]
__timeout__ = 30.0
__max_output_size_kb__ = 500


def fetch_url(
    url: str,
    method: str = "GET",
    headers: str = "",
) -> str:
    """Fetch content from a URL. Headers as 'Key: Value' lines."""
    import requests

    parsed_headers = {}
    if headers:
        for line in headers.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                parsed_headers[key.strip()] = value.strip()

    resp = requests.request(method, url, headers=parsed_headers, timeout=15)

    return f"Status: {resp.status_code}\n\n{resp.text}"
