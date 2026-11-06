# Source map and deliberate adaptations

The selected implementation was reviewed November 6, 2026. Hashes identify private source inputs without publishing that private repository or its history. Example identities and labels preserve comparisons, not live authorization.

| Public file | Original implementation area | Adaptation |
| --- | --- | --- |
| [reference/payroll_key_recovery.py](../reference/payroll_key_recovery.py) | `scripts/payroll_key_recovery.py` | Retain backup/lease/restore/version/receipt logic; remove Azure transport and CLI; replace source identities with examples |
| [reference/test_payroll_key_recovery.py](../reference/test_payroll_key_recovery.py) | `scripts/test_payroll_key_recovery.py` | Neutral example identifiers/labels; logic retained |
| [scripts/backup-postgres.sh](../scripts/backup-postgres.sh) | `platform/backstage/hosting/vm/backup-postgres.sh` | Neutral example identifiers/labels; logic retained |
| [scripts/check-restore.sh](../scripts/check-restore.sh) | `platform/backstage/hosting/vm/check-restore.sh` | Neutral example identifiers/labels; logic retained |
| [scripts/snapshot_cluster.py](../scripts/snapshot_cluster.py) | `platform/backstage/hosting/vm/snapshot_cluster.py` | Neutral example identifiers/labels; logic retained |

Key backup/restore/lease logic and original tests are retained. The actual Azure HTTP credential adapter and CLI are omitted so the public default cannot call the source vault. Fake wrap/unwrap is not real cryptographic acceptance. Related Terraform adapts actual backup-only key permission and storage/retention boundaries.

[Machine source hashes](source-map.json) · [Validation and limits](VALIDATION.md)

PostgreSQL helpers use neutral portal prefixes consistently; an explicit ALLOW_CLOUD_BACKUP opt-in guard is added to the public uploader. New public inventory tests use mocked subprocess results; they are not original production tests.

Related Terraform/reference provenance is recorded separately in the machine map. Parameterized/portable roots retain their own integration boundaries; they are not identical copies of the full deployed infrastructure.
