"""Run GitHub CLI (gh) commands.

Requires: gh CLI installed and authenticated.
No external Python dependencies — uses subprocess.
"""

__tags__ = ["github", "cli"]
__timeout__ = 60.0


def run_gh(
    args: str,
) -> str:
    """Run a GitHub CLI command. Pass arguments as a single string (e.g. 'pr list --repo owner/repo')."""
    import shlex
    import subprocess

    if not args or not args.strip():
        return "Error: args is required (e.g. 'pr list --repo owner/repo')"

    blocked = {"auth", "ssh-key", "gpg-key", "secret set", "variable set"}
    first_words = args.strip().lower()
    for b in blocked:
        if first_words.startswith(b):
            return f"Error: '{b}' subcommand is blocked for safety"

    cmd = ["gh"] + shlex.split(args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=55,
        )
    except FileNotFoundError:
        return "Error: gh CLI not found. Install from https://cli.github.com/"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 55 seconds"

    output = result.stdout.strip()
    error = result.stderr.strip()

    if result.returncode != 0:
        return f"Error (exit {result.returncode}):\n{error or output}"

    return output or "(no output)"
