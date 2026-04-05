"""Execute read-only queries on PostgreSQL.

Requires: psycopg2-binary
"""

__tags__ = ["database", "read"]
__timeout__ = 30.0
__rate_limit__ = "30/min"


def query_postgres(
    query: str,
    connection_string: str = "",
) -> str:
    """Execute a read-only SQL query on PostgreSQL.

    Connection string format: postgresql://user:pass@host:5432/dbname
    Falls back to DATABASE_URL env var if connection_string is empty.
    Only SELECT queries are allowed.
    """
    import os

    conn_str = connection_string or os.environ.get("DATABASE_URL", "")
    if not conn_str:
        return "Error: No connection string provided and DATABASE_URL not set"

    query_upper = query.strip().upper()
    if not query_upper.startswith("SELECT") and not query_upper.startswith("WITH"):
        return "Error: Only SELECT/WITH queries are allowed"

    import psycopg2

    conn = psycopg2.connect(conn_str)
    try:
        conn.set_session(readonly=True, autocommit=True)
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
