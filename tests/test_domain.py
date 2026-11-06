import sqlite3, tempfile, unittest
from pathlib import Path
from lab.domain import backup, restore, inventory


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = sqlite3.connect(self.root / "live.db")
        self.source.executescript(
            "create table records(id integer primary key);insert into records values(1),(2);"
        )
        self.hash = backup(self.source, self.root / "backup.db")

    def tearDown(self):
        self.source.close()
        self.temp.cleanup()

    def test_inventory(self):
        self.assertEqual(inventory(self.source), {"records": 2})

    def test_restore(self):
        self.assertEqual(
            restore(self.root / "backup.db", self.hash, self.root / "restore.db"),
            {"records": 2},
        )

    def test_no_overwrite(self):
        with self.assertRaises(FileExistsError):
            restore(self.root / "backup.db", self.hash, self.root / "live.db")
        self.assertEqual(inventory(self.source), {"records": 2})

    def test_no_self_restore(self):
        with self.assertRaises(ValueError):
            restore(self.root / "backup.db", self.hash, self.root / "backup.db")

    def test_bad_hash(self):
        with self.assertRaises(ValueError):
            restore(self.root / "backup.db", "0" * 64, self.root / "restore.db")
        self.assertFalse((self.root / "restore.db").exists())

    def test_backup_no_overwrite(self):
        with self.assertRaises(FileExistsError):
            backup(self.source, self.root / "backup.db")

    def test_database_integrity_not_only_checksum(self):
        import hashlib

        broken = self.root / "broken.db"
        broken.write_bytes(b"not a database")
        with self.assertRaises(sqlite3.DatabaseError):
            restore(
                broken,
                hashlib.sha256(broken.read_bytes()).hexdigest(),
                self.root / "restore.db",
            )
        self.assertFalse((self.root / "restore.db").exists())
