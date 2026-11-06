"""Portable backup integrity and isolated restore rehearsal."""

import hashlib
from pathlib import Path
import sqlite3
import tempfile
import time
from contextlib import closing


def inventory(connection):
    tables = [
        r[0]
        for r in connection.execute(
            "select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name"
        )
    ]
    # Names come from the database, but still quote identifiers correctly.
    return {
        name: connection.execute(
            'select count(*) from "' + name.replace('"', '""') + '"'
        ).fetchone()[0]
        for name in tables
    }


def backup(source, destination):
    destination = Path(destination)
    with destination.open("xb"):
        pass
    try:
        with closing(sqlite3.connect(destination)) as target:
            source.backup(target)
        return hashlib.sha256(destination.read_bytes()).hexdigest()
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def restore(archive, expected_hash, destination):
    archive = Path(archive)
    destination = Path(destination)
    if archive.resolve() == destination.resolve():
        raise ValueError("Restore target must be isolated")
    data = archive.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_hash:
        raise ValueError("Backup checksum mismatch")
    # Exclusive creation prevents overwriting the live database or another drill.
    with destination.open("xb") as file:
        file.write(data)
    try:
        with closing(sqlite3.connect(destination)) as restored:
            if restored.execute("pragma integrity_check").fetchone()[0] != "ok":
                raise ValueError("Database integrity check failed")
            return inventory(restored)
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def demo():
    start = time.perf_counter()
    checks = []
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        with closing(sqlite3.connect(root / "source.db")) as source:
            source.executescript(
                "create table records(id integer primary key,state text);insert into records values(1,'approved'),(2,'pending');"
            )
            before = inventory(source)
            proof = backup(source, root / "backup.db")
            recovered = restore(root / "backup.db", proof, root / "isolated-restore.db")
            checks.append(
                {
                    "name": "Restored table counts match captured inventory",
                    "passed": before == recovered,
                    "detail": "Integrity check and application-level row counts agree",
                }
            )
            checks.append(
                {
                    "name": "Live source remains readable and unchanged",
                    "passed": inventory(source) == before,
                    "detail": "Restore uses a different exclusive target",
                }
            )
            for name, archive, destination in [
                (
                    "Existing target cannot be overwritten",
                    root / "backup.db",
                    root / "source.db",
                ),
                (
                    "Backup cannot restore over itself",
                    root / "backup.db",
                    root / "backup.db",
                ),
            ]:
                try:
                    restore(archive, proof, destination)
                    passed = False
                except (ValueError, FileExistsError):
                    passed = True
                checks.append(
                    {
                        "name": name,
                        "passed": passed,
                        "detail": "Expected recovery guard observed",
                    }
                )
            corrupted = root / "corrupt.db"
            corrupted.write_bytes((root / "backup.db").read_bytes() + b"changed")
            try:
                restore(corrupted, proof, root / "bad-restore.db")
                blocked = False
            except ValueError:
                blocked = True
            checks.append(
                {
                    "name": "Corrupt archive rejected before restore",
                    "passed": blocked and not (root / "bad-restore.db").exists(),
                    "detail": "SHA-256 mismatch prevents target creation",
                }
            )
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    return {
        "checks": checks,
        "metrics": [
            {"label": "Rows recovered", "value": "2", "detail": "Synthetic database"},
            {
                "label": "Local drill duration",
                "value": str(elapsed) + " ms",
                "detail": "Measured; not a cloud RTO",
            },
            {
                "label": "Overwrite attempts blocked",
                "value": "2",
                "detail": "Separate-target safeguards",
            },
            {
                "label": "Cloud cost",
                "value": "None",
                "detail": "Temporary local files only",
            },
        ],
        "records": [
            ["backup.db", "Verified", proof[:16]],
            [
                "isolated-restore.db",
                "Recovered",
                str(recovered["records"]) + " application rows",
            ],
            ["corrupt.db", "Rejected", "Checksum failed; no restore target created"],
        ],
    }
