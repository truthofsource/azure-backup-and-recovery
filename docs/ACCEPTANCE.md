# Recovery acceptance: distinguish each layer

**Terms used here:** A fixture is test data or a test setup used instead of real business records. Terraform state is its record of the cloud resources it manages.

| Layer | Historical platform evidence | This project's validation | Still separate |
| --- | --- | --- | --- |
| Payroll key used to protect the data key | September private disposable-vault restore and test-only cryptographic check; November ordinary scheduled coverage observations | Eleven original orchestration tests with fake HTTP | New live restore, real current key inventory and fresh receipt |
| Engineering portal | Checksum/inventory PostgreSQL recovery, temporary recovery host and engineer sign-in/reboot checks recorded | Actual helper source; local SQLite guards | Fresh PostgreSQL/container/VM restore on this source |
| SQL business records | Isolated PITR rehearsal procedure prepared | No Azure SQL restore executed | Exact source/point, custodian-only target, schema/aggregate verification |
| Uploaded documents | Fixture version/hash recovery preparation and historical version-recovery pattern | Source/docs and local checksum safeguards | Current end-to-end restored bytes, metadata, quarantine and ownership acceptance |
| Terraform state | Versioning/soft-delete protection accepted for selected state store | No real backend lease/restore exercise | Synthetic isolated backend, lineage/serial/resource checks and real lease contention |

These statements come from maintained platform runbooks, not new cloud observations. No production rollback or restore is implied. Dates belong to their original acceptance. RPO/RTO targets must be business-owned and measured in a fresh representative rehearsal.
