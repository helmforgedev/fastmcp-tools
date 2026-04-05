"""Execute read-only queries on MySQL.

Requires: pymysql
"""

__tags__ = ["database", "read"]
__timeout__ = 30.0
__rate_limit__ = "30/min"


def query_mysql(
    query: str,
    host: str = "",
    port: int = 3306,
    user: str = "",
    password: str = "",
    database: str = "",
) -> str:
    """Execute a read-only SQL query on MySQL.

    Falls back to MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD,
    MYSQL_DATABASE env vars if parameters are empty.
    Only SELECT queries are allowed.
    """
    import os

    host = host or os.environ.get("MYSQL_HOST", "localhost")
    port = port or int(os.environ.get("MYSQL_PORT", "3306"))
    user = user or os.environ.get("MYSQL_USER", "root")
    password = password or os.environ.get("MYSQL_PASSWORD", "")
    database = database or os.environ.get("MYSQL_DATABASE", "")

    query_upper = query.strip().upper()
    if not query_upper.startswith("SELECT") and not query_upper.startswith("WITH"):
        return "Error: Only SELECT/WITH queries are allowed"

    import pymysql

    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        read_timeout=15,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            columns = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()

            lines = [" | ".join(columns)]
            lines.append("-" * len(lines[0]))
            for row in rows[:100]:
                lines.append(" | ".join(str(v) for v in row))

            if len(rows) > 100:
                lines.append(f"... ({len(rows)} total rows, showing first 100)")

            return "\n".join(lines)
    finally:
        conn.close()
