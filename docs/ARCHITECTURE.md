# Recovery architecture

The operational system uses application-level envelope encryption. A restored database still needs wrapped DEKs, exact Key Vault versions, nonce/tag, stable authenticated context and compatible code. Uploaded evidence additionally needs Blob bytes, version/ETag, ownership and authoritative scan state. Terraform state is a separate control-plane recovery concern.

The actual key-backup job has source-key metadata/backup permission and backup-container read/write/lease operations. It does not need source unwrap, rotation or deletion. The manual restore role is different: inspect a disposable private target, restore protected bytes and test source wrap/target unwrap using synthetic material. Neither role is an employee's business-data permission.

The PostgreSQL dump omits role password hashes. Environment, TLS state, runtime secrets and private engineer roster have a separate protected recovery process. Do not store them alongside this public reference or assume a database dump recreates them.

The parameterized Terraform exposes storage/logging, optional isolated compute and an opt-in backup-only exact-key grant. It does not commission production private routes, the six-hour job, event subscriptions or live recovery permissions. Read [the acceptance matrix](ACCEPTANCE.md).
