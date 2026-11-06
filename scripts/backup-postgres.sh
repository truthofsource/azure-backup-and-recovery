#!/usr/bin/env bash
# Run on the reviewed portal VM only after the backup account/container and
# container-scoped managed-identity role are live. No account key or SAS is used.
set -euo pipefail
umask 077

[[ "${ALLOW_CLOUD_BACKUP:-false}" == "true" ]] || { echo "Set ALLOW_CLOUD_BACKUP=true only on the separately authorized backup host." >&2; exit 2; }

: "${PORTAL_BACKUP_CONTAINER_URL:?Set the exact HTTPS backup container URL}"
if [[ ! "$PORTAL_BACKUP_CONTAINER_URL" =~ ^https://[a-z0-9]{3,24}\.blob\.core\.windows\.net/database-backups$ ]]; then
  echo 'Backup destination must be the exact database-backups Blob container URL.' >&2
  exit 2
fi

postgres_container="${PORTAL_POSTGRES_CONTAINER:-portal-postgres}"
if [[ ! "$postgres_container" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$ ]]; then
  echo 'Invalid PostgreSQL container name.' >&2
  exit 2
fi

for executable in docker azcopy gzip sha256sum mktemp; do
  command -v "$executable" >/dev/null || { echo "Missing $executable" >&2; exit 2; }
done

work_dir="$(mktemp -d)"
trap 'rm -f -- "$work_dir"/*; rmdir -- "$work_dir"' EXIT
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
dump_name="portal-${stamp}.sql.gz"
dump_path="$work_dir/$dump_name"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
inventory_path="$work_dir/${dump_name%.sql.gz}.inventory.json"
python3 "$script_dir/snapshot_cluster.py" "$postgres_container" "$inventory_path"

# Dump all plugin databases and global roles, but omit password hashes. The
# restore procedure recreates credentials from separately held configuration.
docker exec -u postgres "$postgres_container" pg_dumpall --clean --if-exists --no-role-passwords | gzip -c > "$dump_path"
gzip -t "$dump_path"
(cd "$work_dir" && sha256sum "$dump_name" > "$dump_name.sha256")

azcopy login --identity >/dev/null
azcopy copy "$dump_path" "$PORTAL_BACKUP_CONTAINER_URL/$dump_name" --from-to LocalBlob --overwrite=false
azcopy copy "$dump_path.sha256" "$PORTAL_BACKUP_CONTAINER_URL/$dump_name.sha256" --from-to LocalBlob --overwrite=false
azcopy copy "$inventory_path" "$PORTAL_BACKUP_CONTAINER_URL/$(basename -- "$inventory_path")" --from-to LocalBlob --overwrite=false
echo "Uploaded and checksum-recorded $dump_name"
