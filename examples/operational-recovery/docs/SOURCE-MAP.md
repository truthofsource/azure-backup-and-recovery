# Source map and deliberate adaptations

The selected implementation was reviewed November 6, 2026. Hashes identify private source inputs without publishing that private repository or its history. Example identities and labels preserve comparisons, not live authorization.

| Public file | Original implementation area | Adaptation |
| --- | --- | --- |
| [reference/deliveryReports.ts](../reference/deliveryReports.ts) | `apps/api/src/email/deliveryReports.ts` | Neutral example identifiers/labels; portable dependency boundary |
| [reference/deliveryReports.test.ts](../reference/deliveryReports.test.ts) | `apps/api/src/email/deliveryReports.test.ts` | Neutral example identifiers/labels; portable dependency boundary |
| [reference/contactIdentity.ts](../reference/contactIdentity.ts) | `apps/api/src/provider/attendanceDelivery.ts` | Extract original email normalization/hash; SMS adapter explicitly unavailable |
| [reference/noticeEmailDelivery.ts](../reference/noticeEmailDelivery.ts) | `apps/api/src/contracts/noticeEmailDelivery.ts` | Neutral example identifiers/labels; portable dependency boundary |
| [reference/noticeEmailDelivery.test.ts](../reference/noticeEmailDelivery.test.ts) | `apps/api/src/contracts/noticeEmailDelivery.test.ts` | Neutral example identifiers/labels; portable dependency boundary |
| [scripts/backup-postgres.sh](../scripts/backup-postgres.sh) | `platform/backstage/hosting/vm/backup-postgres.sh` | Neutral example identifiers/labels; logic retained |
| [scripts/check-restore.sh](../scripts/check-restore.sh) | `platform/backstage/hosting/vm/check-restore.sh` | Neutral example identifiers/labels; logic retained |
| [scripts/snapshot_cluster.py](../scripts/snapshot_cluster.py) | `platform/backstage/hosting/vm/snapshot_cluster.py` | Neutral example identifiers/labels; logic retained |

The report reader retains its real bounded correlation and masking logic. The default Azure credential adapter is replaced by an explicit injected-token boundary; original tests inject fake token/HTTP dependencies. SMS normalization is intentionally unavailable in this email-only extraction.

[Machine source hashes](source-map.json) · [Validation and limits](VALIDATION.md)

PostgreSQL helpers use neutral portal prefixes consistently; an explicit ALLOW_CLOUD_BACKUP opt-in guard is added to the public uploader. New public inventory tests use mocked subprocess results; they are not original production tests.

The source map records where the Terraform and other reference files came from. The reusable examples still need their own connection tests and are not complete copies of the deployed setup.
