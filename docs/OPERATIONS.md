# Recovery operations and troubleshooting

**Terms used here:** Terraform state is its record of the cloud resources it manages.

| Observation | Meaning | Next check |
| --- | --- | --- |
| Coverage current | Known versions and verified retained backup agree within the allowed age | Confirm ordinary check history and backup age; no forced backup needed |
| Key changed during backup | Versions/enable flags changed between inventory and backup | No success/latest pointer; reconcile the new state before a limited retry |
| Lost Blob response | A write may have completed | Read back exact expected bytes before deciding whether another write is needed |
| Lease conflict | Another coverage worker can own the lease | Treat overlap separately from permission/network failure |
| Hash mismatch | Backup bytes no longer match trusted receipt | Stop before restore and preserve evidence |
| Target already has key | Could be earlier completed/uncertain restore | Reconcile privately; never overwrite blindly |
| Partial restore | Disabled versions were not cryptographically exercised | Retain explicit partial status; do not label all versions verified |
| Restore passed, cleanup pending | Data/crypto acceptance and resource cleanup are different steps | Remove only owned target/grants and verify source unchanged |

Database restore needs a consistent source snapshot and a quiet/controlled comparison window: the helper's separate inventory and dump can diverge if application writes continue. Row counts detect many mismatches but are not row-by-row content proofs. Verify schema/constraints and the actual business recovery scope.

Restored documents must preserve owner/revision/ETag relationships and the scan verdict's byte identity. Restored Terraform state needs lineage/serial/resource checks and isolated backend locking. A checksum or local file copy does not prove Azure lease behavior.
