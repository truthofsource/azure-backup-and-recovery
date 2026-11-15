"""Inventory table row counts for an exact local PostgreSQL container.

This retains technical identifiers/counts only, never row values or credentials.
Use the same helper before backup and after isolated restore for comparison.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess


def snapshot(container, user):
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", container) or not re.fullmatch(r"[a-zA-Z0-9_]+", user):
        raise ValueError("Invalid local container or database login")

    def query(database, sql):
        result = subprocess.run(["docker", "exec", "-i", "-u", "postgres", container, "psql", "-X", "-U", user,
            "-d", database, "-At", "-v", "ON_ERROR_STOP=1"], input=sql, text=True, capture_output=True)
        if result.returncode:
            raise ValueError("Technical database inventory failed")
        return result.stdout.splitlines()

    databases = query("postgres", "SELECT datname FROM pg_database WHERE NOT datistemplate AND datname NOT IN ('postgres','restore_admin') ORDER BY datname;")
    counts = {}
    for database in databases:
        if not database.startswith("portal"):
            raise ValueError("Unexpected non-portal database")
        rows = query(database, r"""SELECT format('SELECT %L, count(*) FROM %I.%I;',
             n.nspname || '.' || c.relname, n.nspname, c.relname)
             FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
             WHERE c.relkind IN ('r','p') AND n.nspname NOT LIKE 'pg_%'
             AND n.nspname <> 'information_schema' ORDER BY n.nspname,c.relname
             \gexec
             """)
        counts[database] = {name: int(count) for name, count in (line.rsplit("|", 1) for line in rows)}
    if not counts or not any(counts.values()):
        raise ValueError("No application tables found")
    return {"schema": "portal.cluster-inventory.v1", "databases": counts}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("container")
    parser.add_argument("output", type=Path)
    parser.add_argument("--user", default="postgres")
    args = parser.parse_args()
    result = snapshot(args.container, args.user)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    args.output.chmod(0o600)
    print(json.dumps({"status": "inventoried", "database_count": len(result["databases"]),
        "table_count": sum(len(tables) for tables in result["databases"].values())}))
