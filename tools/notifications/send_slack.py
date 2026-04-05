"""Send messages to Slack via webhook.

Requires: requests
"""

__tags__ = ["notifications", "write"]
__timeout__ = 15.0
__rate_limit__ = "10/min"


def send_slack(
    message: str,
    webhook_url: str = "",
    channel: str = "",
) -> str:
    """Send a message to Slack via incoming webhook.

    Falls back to SLACK_WEBHOOK_URL env var if webhook_url is empty.
    """
    import os

    import requests

    url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL", "")
    if not url:
        return "Error: No webhook URL provided and SLACK_WEBHOOK_URL not set"

    payload = {"text": message}
    if channel:
        payload["channel"] = channel

    resp = requests.post(url, json=payload, timeout=10)

    if resp.status_code == 200 and resp.text == "ok":
        return "Message sent to Slack"
    return f"Slack error: {resp.status_code} {resp.text}"
