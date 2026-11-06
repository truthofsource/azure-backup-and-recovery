#!/usr/bin/env bash
# Rehearse a backup in a disposable, network-isolated PostgreSQL container.
# Never point this script at the live database container.
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo 'Usage: check-restore.sh <dump.sql.gz> <dump.sql.gz.sha256> [expected-inventory.json]' >&2
  exit 2
fi
dump_path="$(realpath -- "$1")"
checksum_path="$(realpath -- "$2")"
[[ "$dump_path" == *.sql.gz && "$checksum_path" == "$dump_path.sha256" ]] || {
  echo 'Expected a matching compressed dump and checksum sidecar.' >&2
  exit 2
}
for executable in docker gzip sha256sum realpath; do
  command -v "$executable" >/dev/null || { echo "Missing $executable" >&2; exit 2; }
done
if [[ $# -eq 3 ]]; then
  expected_inventory="$(realpath -- "$3")"
  [[ -f "$expected_inventory" ]] || { echo 'Inventory file missing' >&2; exit 2; }
  command -v python3 >/dev/null || { echo 'Python required for inventory comparison' >&2; exit 2; }
fi
(cd "$(dirname "$dump_path")" && sha256sum -c "$(basename "$checksum_path")")
gzip -t "$dump_path"

: "${PORTAL_RESTORE_POSTGRES_IMAGE:?Set a reviewed PostgreSQL 16 image digest}"
if [[ ! "$PORTAL_RESTORE_POSTGRES_IMAGE" =~ ^postgres@sha256:[a-f0-9]{64}$ ]]; then
  echo 'Restore image must be pinned as postgres@sha256:<64 hex chars>.' >&2
  exit 2
fi

restore_container="portal-restore-$$"
trap 'docker rm -f "$restore_container" >/dev/null 2>&1 || true' EXIT
docker run -d --name "$restore_container" --network none \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -e POSTGRES_USER=restore_admin -e POSTGRES_DB=restore_admin \
  "$PORTAL_RESTORE_POSTGRES_IMAGE" >/dev/null
for attempt in {1..60}; do
  if docker exec -u postgres "$restore_container" pg_isready -h 127.0.0.1 -U restore_admin -d restore_admin -q; then break; fi
  if [[ "$attempt" -eq 60 ]]; then echo 'Disposable PostgreSQL did not start.' >&2; exit 1; fi
  sleep 1
done
gzip -dc "$dump_path" | docker exec -i -u postgres "$restore_container" \
  psql -X -U restore_admin -v ON_ERROR_STOP=1 -d restore_admin >/dev/null
database_count="$(docker exec -u postgres "$restore_container" psql -U restore_admin -At -d restore_admin -c \
  "select count(*) from pg_database where datistemplate = false and datname not in ('postgres', 'restore_admin')")"
[[ "$database_count" =~ ^[0-9]+$ && "$database_count" -gt 0 ]] || {
  echo 'Restored cluster contains no portal plugin database.' >&2
  exit 1
}
if [[ $# -eq 3 ]]; then
  script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  python3 - "$restore_container" "$expected_inventory" "$script_dir" <<'PY'
import json
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[3])
from snapshot_cluster import snapshot
expected = json.loads(Path(sys.argv[2]).read_text())
actual = snapshot(sys.argv[1], 'restore_admin')
if actual != expected:
    raise SystemExit('Restore inventory mismatch: database/table counts differ; no row values displayed')
print('Restored database, table and row-count inventories match the saved source snapshot.')
PY
fi
echo "Restore rehearsal passed: $database_count application databases in isolated container."
