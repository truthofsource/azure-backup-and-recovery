# Actual PostgreSQL operational helpers

These helpers are extracted from the engineering portal's VM backup/recovery implementation. Public resource/container prefixes use portal; the explicit ALLOW_CLOUD_BACKUP guard is added for this standalone publication. The original dump, checksum, inventory and isolated-restore logic is retained.

- snapshot_cluster.py reads technical database/table counts, not row values. Expected application database names start with portal.
- backup-postgres.sh requires ALLOW_CLOUD_BACKUP=true and PORTAL_BACKUP_CONTAINER_URL; uses managed-identity AzCopy, omits role passwords and refuses overwrite. It can upload real data if run on an authorized live host, so do not run it merely for a local portfolio check.
- check-restore.sh requires PORTAL_RESTORE_POSTGRES_IMAGE=postgres@sha256:<reviewed digest>, an existing dump and its matching checksum. It restores into a disposable --network none container, exposes no host port and optionally compares saved inventory.

```bash
bash -n scripts/backup-postgres.sh scripts/check-restore.sh
# Separate authorized local restore, after obtaining a reviewed image and fixture:
export PORTAL_RESTORE_POSTGRES_IMAGE='postgres@sha256:<reviewed-digest>'
bash scripts/check-restore.sh dump.sql.gz dump.sql.gz.sha256 expected.inventory.json
```

Syntax inspection and mocked inventory tests do not claim a current PostgreSQL restore. Trust auth belongs only to the isolated disposable container. Capture inventory/dump while writes are controlled; separate reads can otherwise disagree. Row counts are not row-by-row integrity proofs. Runtime credentials, TLS state and private configuration are restored separately.
