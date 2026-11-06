# Scaling, costs, strengths and tradeoffs

| Design | Strength | Tradeoff | Growth response |
| --- | --- | --- | --- |
| Six-hour key coverage checks | Finds changed versions without a full backup every wake | Check frequency is not an end-to-end RPO guarantee | Measure coverage age and missing/silent executions |
| Backup on version changes or seven-day age | Limits redundant full key exports | Source changes during export need race detection | Keep before/after inventory, finite lease and bounded retries |
| Exact-version receipts | Makes recovery dependencies explicit | Historical backups depend on retained key material and compatible metadata | Inventory versions across data and backup retention |
| Isolated restore targets | Protects live bindings | Temporary compute, network and custodian grants cost money | Bound lifetime, size and cleanup ownership |
| PostgreSQL dump and inventory | Portable application-level evidence | Inventory/dump need consistency control; row counts are not content checks | Quiet writes or use a stronger snapshot strategy for larger systems |
| Protected storage and logs | Recoverable history and visible failures | Version retention, ingestion and stored backups add cost | Separate operational retention from long-term recovery requirements |

Use business-owned recovery tiers. RPO is acceptable data loss; RTO is acceptable recovery time. Observe real restore-point lag and measured restore duration rather than claiming an SLA from a timer interval or local milliseconds.

Key Vault protected backups are limited to the same subscription and Azure geography on restore. More than 500 versions exceeds the documented per-object backup capability; old versions cannot be individually deleted. Protect any restored copies because disabling the original does not revoke those copies. A replacement-vault recovery needs tested application URI/metadata handling.

VM deallocation can remove compute charges while disks, storage, logs and networking still cost money. This portfolio starts no service and establishes no new paid endpoint or SIEM route.
