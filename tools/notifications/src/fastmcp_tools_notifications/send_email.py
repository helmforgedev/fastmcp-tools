"""Send email via SMTP.

No external dependencies required (uses stdlib smtplib).
"""

__tags__ = ["notifications", "write"]
__timeout__ = 30.0
__rate_limit__ = "5/min"


def send_email(
    to: str,
    subject: str,
    body: str,
    smtp_host: str = "",
    smtp_port: int = 587,
    smtp_user: str = "",
    smtp_password: str = "",
    from_addr: str = "",
) -> str:
    """Send an email via SMTP.

    Falls back to SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
    SMTP_FROM env vars if parameters are empty.
    """
    import os
    import smtplib
    from email.mime.text import MIMEText

    host = smtp_host or os.environ.get("SMTP_HOST", "")
    port = smtp_port or int(os.environ.get("SMTP_PORT", "587"))
    user = smtp_user or os.environ.get("SMTP_USER", "")
    password = smtp_password or os.environ.get("SMTP_PASSWORD", "")
    sender = from_addr or os.environ.get("SMTP_FROM", user)

    if not host:
        return "Error: No SMTP host provided and SMTP_HOST not set"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    with smtplib.SMTP(host, port, timeout=15) as server:
        server.starttls()
        if user and password:
            server.login(user, password)
        server.send_message(msg)

    return f"Email sent to {to}"
