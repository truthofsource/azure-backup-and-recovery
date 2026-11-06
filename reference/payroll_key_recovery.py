"""Actual recovery orchestration with an injected transport. No Azure HTTP client or CLI included."""
import base64,datetime as dt,hashlib,json,os,re,threading,time,urllib.parse,uuid
SUB="00000000-0000-4000-8000-000000000007"
VAULT="vault-example-source"
KEY="payroll-details-wrapping-key"
ARM="https://management.azure.com"
KV=f"https://{VAULT}.vault.azure.net"
BLOB="https://examplerecoveryprod.blob.core.windows.net/key-backups"
MAX_BYTES=16*1024*1024
class RecoveryError(Exception):
    pass

class HttpFailure(RecoveryError):
    def __init__(self, status):
        self.status = status
        super().__init__(f"http_{status}")

def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def encoded(value):
    return base64.urlsafe_b64encode(value).decode().rstrip("=")

def decoded(value):
    if not isinstance(value, str) or not value or len(value) > MAX_BYTES * 2 or not re.fullmatch(r"[A-Za-z0-9_-]+={0,2}", value):
        raise RecoveryError("invalid_encoded_bytes")
    result = base64.urlsafe_b64decode(value.rstrip("=") + "=" * (-len(value.rstrip("=")) % 4))
    if not result or len(result) > MAX_BYTES:
        raise RecoveryError("invalid_backup_size")
    return result

def emit(event, **values):
    print(json.dumps({"component": "workforce-payroll-recovery", "event": event, "atUtc": stamp(), **values}), flush=True)

def versions(http, vault_url):
    initial = f"{vault_url}/keys/{KEY}/versions?api-version=7.4"
    url, seen, items = initial, set(), {}
    while url:
        p = urllib.parse.urlsplit(url)
        if p.scheme != "https" or p.hostname != urllib.parse.urlsplit(vault_url).hostname or p.port not in [None, 443] or p.username or p.password or p.path != f"/keys/{KEY}/versions" or p.fragment or url in seen:
            raise RecoveryError("invalid_version_continuation")
        seen.add(url)
        page = http.json(url)
        for item in page["value"]:
            kid = item["kid"]
            key = urllib.parse.urlsplit(kid)
            if key.scheme != "https" or key.hostname != urllib.parse.urlsplit(vault_url).hostname or key.port not in [None, 443] or key.username or key.password or key.query or key.fragment or not re.fullmatch(rf"/keys/{KEY}/[a-f0-9]{{32}}", key.path):
                raise RecoveryError("invalid_key_version")
            enabled = item["attributes"].get("enabled", True)
            if type(enabled) is not bool: raise RecoveryError("invalid_key_attributes")
            items[key.path.rsplit("/", 1)[1]] = {"enabled": enabled}
        if len(items) > 500 or len(seen) > 100:
            raise RecoveryError("version_limit_exceeded")
        url = page.get("nextLink")
    if not items:
        raise RecoveryError("key_versions_missing")
    return dict(sorted(items.items()))

class BlobStore:
    def __init__(self, http):
        self.http = http

    def url(self, name):
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", name) or ".." in name:
            raise RecoveryError("invalid_blob_name")
        return BLOB + "/" + name

    def get(self, name):
        try:
            return self.http.request(self.url(name))[0]
        except HttpFailure as error:
            if error.status == 404: return None
            raise

    def put(self, name, value, create=True, metadata=None):
        headers = {"x-ms-blob-type": "BlockBlob", "x-ms-blob-content-type": "application/octet-stream"}
        if create: headers["If-None-Match"] = "*"
        for key, content in (metadata or {}).items(): headers["x-ms-meta-" + key] = content
        try:
            self.http.request(self.url(name), "PUT", value, headers)
        except RecoveryError:
            # A lost response may follow a successful create; do not repeat a write.
            if self.get(name) != value: raise
        if self.get(name) != value:
            raise RecoveryError("blob_readback_mismatch")

    def document(self, name):
        value = self.get(name)
        return None if value is None else json.loads(value)

class Lease:
    def __init__(self, store):
        self.store, self.id = store, str(uuid.uuid4())
        self.stop = threading.Event()
        self.failed = False

    def action(self, action):
        headers = {"x-ms-lease-action": action, "x-ms-lease-id": self.id}
        if action == "acquire": headers.update({"x-ms-proposed-lease-id": self.id, "x-ms-lease-duration": "60"}); headers.pop("x-ms-lease-id")
        return self.store.http.request(self.store.url("backup.lock") + "?comp=lease", "PUT", b"", headers)

    def __enter__(self):
        # Existing lock bytes are fixed; create-only PUT does not replace the blob.
        self.store.put("backup.lock", b"workforce-payroll-key-backup-lock")
        try:
            self.action("acquire")
        except HttpFailure as error:
            if error.status == 409: raise RecoveryError("backup_already_running") from None
            raise
        self.thread = threading.Thread(target=self.renew, daemon=True); self.thread.start()
        return self

    def renew(self):
        while not self.stop.wait(20):
            try: self.action("renew")
            except RecoveryError: self.failed = True; return

    def check(self):
        if self.failed: raise RecoveryError("backup_lease_lost")
        # Confirm ownership and renew before each write checkpoint.
        self.action("renew")

    def __exit__(self, *args):
        self.stop.set(); self.thread.join(timeout=45)
        try: self.action("release")
        except RecoveryError: emit("lease_release_pending")

def valid_receipt(receipt):
    if not isinstance(receipt, dict) or receipt.get("sourceVault") != VAULT or receipt.get("keyName") != KEY or receipt.get("readbackVerified") is not True:
        raise RecoveryError("invalid_backup_receipt")
    if not re.fullmatch(r"payroll-details-wrapping-key-[a-zA-Z0-9-]+\.backup", receipt.get("blobName", "")) or not re.fullmatch(r"[a-f0-9]{64}", receipt.get("sha256", "")):
        raise RecoveryError("invalid_backup_receipt")
    if not isinstance(receipt.get("versions"), dict) or not receipt["versions"] or len(receipt["versions"]) > 500:
        raise RecoveryError("invalid_backup_receipt")
    for version, attributes in receipt["versions"].items():
        if not re.fullmatch(r"[a-f0-9]{32}", version) or not isinstance(attributes, dict) or type(attributes.get("enabled")) is not bool:
            raise RecoveryError("invalid_backup_receipt")
    instant = dt.datetime.fromisoformat(receipt["createdAtUtc"])
    if instant.tzinfo is None or instant > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
        raise RecoveryError("invalid_backup_timestamp")
    return instant

def backup(http, force=False, max_age_days=7, lease_factory=Lease):
    store = BlobStore(http)
    with lease_factory(store) as lease:
        current = versions(http, KV)
        latest = store.document("latest.json")
        if latest:
            instant = valid_receipt(latest)
            if not force and latest["versions"] == current and dt.datetime.now(dt.timezone.utc) - instant < dt.timedelta(days=max_age_days):
                existing = store.get(latest["blobName"])
                if existing is None or hashlib.sha256(existing).hexdigest() != latest["sha256"]:
                    raise RecoveryError("retained_backup_missing_or_changed")
                lease.check(); emit("coverage_current", versionCount=len(current), backupAtUtc=latest["createdAtUtc"])
                return latest
        lease.check()
        payload = http.json(f"{KV}/keys/{KEY}/backup?api-version=7.4", "POST", {})
        data = decoded(payload["value"])
        if versions(http, KV) != current:
            raise RecoveryError("key_changed_during_backup")
        lease.check()
        run = uuid.uuid4().hex
        name = f"{KEY}-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{run}.backup"
        digest = hashlib.sha256(data).hexdigest()
        store.put(name, data, metadata={"sha256": digest})
        receipt = {"schemaVersion": 1, "sourceVault": VAULT, "keyName": KEY, "blobName": name, "sha256": digest, "receiptName": f"receipts/{run}.json",
                   "bytes": len(data), "versions": current, "createdAtUtc": stamp(), "readbackVerified": True}
        lease.check()
        store.put(f"receipts/{run}.json", json.dumps(receipt, sort_keys=True).encode())
        lease.check()
        store.put("latest.json", json.dumps(receipt, sort_keys=True).encode(), create=False)
        emit("backup_verified", versionCount=len(current), backupAtUtc=receipt["createdAtUtc"], bytes=len(data), sha256=digest, receiptName=receipt["receiptName"])
        return receipt

def restore_target(http, target_resource_id):
    expected = rf"/subscriptions/{SUB}/resourceGroups/rg-example-payroll-recovery-dr-centralus/providers/Microsoft.KeyVault/vaults/(kv-example-payroll-dr-[a-z0-9]{{1,6}})"
    match = re.fullmatch(expected, target_resource_id)
    if not match: raise RecoveryError("disposable_restore_target_required")
    name = match[1]
    target = http.json(ARM + target_resource_id + "?api-version=2023-07-01")
    source = http.json(ARM + f"/subscriptions/{SUB}/resourceGroups/rg-workforce-platform-platform-production-centralus/providers/Microsoft.KeyVault/vaults/{VAULT}?api-version=2023-07-01")
    if target.get("id", "").lower() != target_resource_id.lower() or target.get("location") != source.get("location") or target.get("tags", {}).get("purpose") != "disposable-payroll-key-restore":
        raise RecoveryError("restore_boundary_mismatch")
    properties = target["properties"]
    if properties.get("publicNetworkAccess") != "Disabled" or properties.get("enableRbacAuthorization") is not True:
        raise RecoveryError("restore_vault_must_be_private_rbac")
    url = f"https://{name}.vault.azure.net"
    if properties.get("vaultUri", "").rstrip("/") != url:
        raise RecoveryError("restore_vault_uri_mismatch")
    return url

def restore(http, target_resource_id, receipt_name):
    if not re.fullmatch(r"receipts/[a-f0-9]{32}\.json", receipt_name):
        raise RecoveryError("exact_backup_receipt_required")
    target = restore_target(http, target_resource_id)
    store = BlobStore(http); receipt = store.document(receipt_name)
    if receipt is None: raise RecoveryError("backup_receipt_missing")
    valid_receipt(receipt)
    data = store.get(receipt["blobName"])
    if data is None or hashlib.sha256(data).hexdigest() != receipt["sha256"]:
        raise RecoveryError("backup_checksum_mismatch")
    # Re-running after an uncertain restore must never overwrite an existing key.
    try: http.json(f"{target}/keys/{KEY}?api-version=7.4")
    except HttpFailure as error:
        if error.status != 404: raise
    else: raise RecoveryError("restore_key_already_present_reconcile_privately")
    try:
        http.json(f"{target}/keys/restore?api-version=7.4", "POST", {"value": encoded(data)})
    except RecoveryError:
        # Restore may have succeeded before its response was lost. Reconcile once.
        if versions(http, target) != receipt["versions"]: raise
    if versions(http, target) != receipt["versions"]:
        raise RecoveryError("restored_version_coverage_mismatch")
    tested, skipped = [], []
    for version, attributes in receipt["versions"].items():
        if not attributes["enabled"]:
            skipped.append(version); continue
        plain = os.urandom(32)
        wrapped = http.json(f"{KV}/keys/{KEY}/{version}/wrapkey?api-version=7.4", "POST", {"alg": "RSA-OAEP-256", "value": encoded(plain)})
        unwrapped = http.json(f"{target}/keys/{KEY}/{version}/unwrapkey?api-version=7.4", "POST", {"alg": "RSA-OAEP-256", "value": wrapped["value"]})
        if decoded(unwrapped["value"]) != plain:
            raise RecoveryError("restored_crypto_roundtrip_mismatch")
        tested.append(version)
    if not tested: raise RecoveryError("no_enabled_version_tested")
    result = {"schemaVersion": 1, "atUtc": stamp(), "backupReceipt": receipt_name, "backupSha256": receipt["sha256"],
              "versionCoverageVerified": True, "testedVersions": tested, "disabledVersionsNotTested": skipped,
              "restoreVerified": not skipped, "cleanupPending": True}
    store.put("restore-receipts/" + uuid.uuid4().hex + ".json", json.dumps(result, sort_keys=True).encode())
    emit("restore_verified" if not skipped else "restore_partial", testedVersions=len(tested), disabledVersions=len(skipped))
    return result
