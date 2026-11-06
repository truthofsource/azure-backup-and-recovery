import contextlib
import copy
import hashlib
import io
import json
import unittest
from unittest.mock import patch
from reference import payroll_key_recovery as recovery

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
