import contextlib
import copy
import hashlib
import io
import json
import unittest
from unittest.mock import patch
import payroll_key_recovery as recovery

VERSION = "a" * 32
TARGET = f"/subscriptions/{recovery.SUB}/resourceGroups/rg-example-payroll-recovery-dr-centralus/providers/Microsoft.KeyVault/vaults/kv-example-payroll-dr-test"
TARGET_URL = "https://kv-example-payroll-dr-test.vault.azure.net"


class FakeHttp:
    def __init__(self):
        self.blobs = {}; self.calls = []; self.lost_write = False
        self.target_versions = None; self.changed = False; self.fail_crypto = False
        self.source_versions = {VERSION: {"enabled": True}}
        self.target_private = True

    def request(self, url, method="GET", body=None, headers=None):
        self.calls.append((method, url))
        name = url.removeprefix(recovery.BLOB + "/")
        if "?comp=lease" in name: return b"", {}
        if method == "GET":
            if name not in self.blobs: raise recovery.HttpFailure(404)
            return self.blobs[name], {}
        if method == "PUT":
            if headers.get("If-None-Match") == "*" and name in self.blobs: raise recovery.HttpFailure(412)
            self.blobs[name] = body
            if self.lost_write:
                self.lost_write = False
                raise recovery.RecoveryError("transport_unavailable")
            return b"", {}
        raise AssertionError(method)

    def json(self, url, method="GET", body=None):
        self.calls.append((method, url))
        if url.startswith(recovery.ARM):
            if "kv-example-payroll-dr-test" in url:
                return {"id": TARGET, "location": "centralus", "tags": {"purpose": "disposable-payroll-key-restore"},
                        "properties": {"vaultUri": TARGET_URL + "/", "publicNetworkAccess": "Disabled" if self.target_private else "Enabled", "enableRbacAuthorization": True}}
            return {"location": "centralus"}
        if "/versions?" in url:
            versions = self.target_versions if url.startswith(TARGET_URL) else self.source_versions
            if versions is None: raise recovery.HttpFailure(404)
            return {"value": [{"kid": url.split("/keys/")[0] + f"/keys/{recovery.KEY}/{version}", "attributes": attrs} for version, attrs in versions.items()]}
        if "/backup?" in url:
            if self.changed: self.source_versions["b" * 32] = {"enabled": True}
            return {"value": recovery.encoded(b"encrypted-fixture-backup")}
        if "/keys/restore?" in url:
            self.target_versions = copy.deepcopy(self.source_versions)
            return {}
        if "/wrapkey?" in url:
            self.plain = body["value"]
            return {"value": "wrapped-fixture"}
        if "/unwrapkey?" in url:
            return {"value": recovery.encoded(b"wrong") if self.fail_crypto else self.plain}
        if self.target_versions is None: raise recovery.HttpFailure(404)
        return {"key": {}}


class FakeLease:
    def __init__(self, store): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def check(self): pass


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.http = FakeHttp()
        self.capture = io.StringIO()
        self.logs = contextlib.redirect_stdout(self.capture); self.logs.__enter__()

    def tearDown(self): self.logs.__exit__(None, None, None)

    def backup(self): return recovery.backup(self.http, lease_factory=FakeLease)

    def test_backup_is_private_create_only_and_version_receipted(self):
        receipt = self.backup()
        self.assertEqual(receipt["versions"], {VERSION: {"enabled": True}})
        self.assertEqual(receipt["sha256"], hashlib.sha256(b"encrypted-fixture-backup").hexdigest())
        self.assertEqual(json.loads(self.http.blobs["latest.json"]), receipt)
        self.assertIn(receipt["receiptName"], self.http.blobs)
        self.assertNotIn("encrypted-fixture-backup", self.capture.getvalue())

    def test_current_coverage_skips_backup_and_rotation_creates_new_backup(self):
        first = self.backup(); self.http.calls.clear()
        self.assertEqual(self.backup(), first)
        self.assertFalse(any("/backup?" in url for _, url in self.http.calls))
        self.http.source_versions["b" * 32] = {"enabled": True}
        second = self.backup(); self.assertNotEqual(second["blobName"], first["blobName"])
        self.assertEqual(len(second["versions"]), 2)

    def test_changed_backup_missing_data_and_lost_response(self):
        receipt = self.backup(); self.http.blobs[receipt["blobName"]] = b"changed"
        with self.assertRaisesRegex(recovery.RecoveryError, "retained_backup"): self.backup()
        store = recovery.BlobStore(self.http); self.http.lost_write = True
        store.put("safe.backup", b"fixture")
        self.assertEqual(self.http.blobs["safe.backup"], b"fixture")

    def test_rotation_during_backup_does_not_publish_success(self):
        self.http.changed = True
        with self.assertRaisesRegex(recovery.RecoveryError, "key_changed"): self.backup()
        self.assertNotIn("latest.json", self.http.blobs)

    def test_restore_checks_boundary_checksum_versions_and_crypto(self):
        receipt = self.backup()
        result = recovery.restore(self.http, TARGET, receipt["receiptName"])
        self.assertTrue(result["restoreVerified"])
        self.assertTrue(result["cleanupPending"])
        self.assertEqual(result["testedVersions"], [VERSION])
        with self.assertRaisesRegex(recovery.RecoveryError, "already_present"):
            recovery.restore(self.http, TARGET, receipt["receiptName"])

    def test_restore_rejects_live_public_or_wrong_target_before_restore(self):
        receipt = self.backup()
        with self.assertRaisesRegex(recovery.RecoveryError, "disposable_restore"):
            recovery.restore(self.http, TARGET.replace("kv-example-payroll-dr-test", recovery.VAULT), receipt["receiptName"])
        self.http.target_private = False
        with self.assertRaisesRegex(recovery.RecoveryError, "private_rbac"):
            recovery.restore(self.http, TARGET, receipt["receiptName"])
        self.assertFalse(any("/keys/restore?" in url for _, url in self.http.calls))

    def test_restore_tampering_and_crypto_mismatch_never_claim_success(self):
        receipt = self.backup(); self.http.blobs[receipt["blobName"]] = b"tampered"
        with self.assertRaisesRegex(recovery.RecoveryError, "checksum"):
            recovery.restore(self.http, TARGET, receipt["receiptName"])
        self.http.blobs[receipt["blobName"]] = b"encrypted-fixture-backup"; self.http.fail_crypto = True
        with self.assertRaisesRegex(recovery.RecoveryError, "roundtrip"):
            recovery.restore(self.http, TARGET, receipt["receiptName"])
        self.assertFalse(any(name.startswith("restore-receipts/") for name in self.http.blobs))

    def test_disabled_versions_remain_explicitly_unaccepted(self):
        self.http.source_versions["b" * 32] = {"enabled": False}
        receipt = self.backup(); result = recovery.restore(self.http, TARGET, receipt["receiptName"])
        self.assertFalse(result["restoreVerified"])
        self.assertEqual(result["disabledVersionsNotTested"], ["b" * 32])

    def test_lease_acquire_renew_release_and_lost_lease_fail(self):
        store = recovery.BlobStore(self.http)
        with recovery.Lease(store) as lease:
            lease.check(); lease.failed = True
            with self.assertRaisesRegex(recovery.RecoveryError, "lease_lost"): lease.check()
        actions = [url for method, url in self.http.calls if "?comp=lease" in url]
        self.assertEqual(len(actions), 3)

    def test_source_version_continuation_cannot_redirect(self):
        with patch.object(self.http, "json", return_value={"value": [], "nextLink": "https://attacker.invalid/keys/anything/versions"}):
            with self.assertRaisesRegex(recovery.RecoveryError, "continuation"): recovery.versions(self.http, recovery.KV)

    def test_only_lease_conflict_is_treated_as_overlap(self):
        store = recovery.BlobStore(self.http)
        original = self.http.request
        def conflict(url, method="GET", body=None, headers=None):
            if "?comp=lease" in url and headers.get("x-ms-lease-action") == "acquire":
                raise recovery.HttpFailure(409)
            return original(url, method, body, headers)
        with patch.object(self.http, "request", side_effect=conflict):
            with self.assertRaisesRegex(recovery.RecoveryError, "backup_already_running"):
                with recovery.Lease(store): pass


if __name__ == "__main__": unittest.main()
