"""POST JSON data to a URL.

Requires: requests
"""

__tags__ = ["http", "write"]
__timeout__ = 30.0


def post_json(
    url: str,
    data: str,
    headers: str = "",
) -> str:
    """POST JSON data to a URL. Data should be a valid JSON string."""
    import json

    import requests

    try:
        payload = json.loads(data)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON data: {e}"

    parsed_headers = {"Content-Type": "application/json"}
    if headers:
        for line in headers.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                parsed_headers[key.strip()] = value.strip()

    resp = requests.post(url, json=payload, headers=parsed_headers, timeout=15)

    return f"Status: {resp.status_code}\n\n{resp.text}"
