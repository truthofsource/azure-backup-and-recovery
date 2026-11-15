# Operational Evidence from the Running Platform

**Terms used here:** An artifact is a file produced for a release, such as an application ZIP or container image. Provenance means the record of where a release came from and how it was produced.

The platform separates application outcomes from transport outcomes. An accepted email ledger entry means the provider accepted the request; it does not establish delivery. The actual report reader correlates provider ID, recipient hash and event time against the configured Communication Services resource and Log Analytics workspace.

Its bounded read rejects arbitrary resources/IDs, caps row counts and response size, caches the query for sixty seconds, masks recipients for restricted viewers and refuses to call missing/incomplete telemetry delivered. It overlays a transport report without rewriting the send ledger or sending a retry. The source route's authentication/authorization remains a separate layer.

The engineering portal includes tools to save a PostgreSQL backup, record its contents and practise restoring it in a separate container. The backup contains plugin databases and shared database roles, but leaves out role password hashes. Credentials, the engineer list, settings and HTTPS certificate data need their own protected recovery process. Earlier server-recovery and sign-in tests do not prove that every future database, document or Terraform-state restore will work.

The portfolio keeps the local SQLite rehearsal as a small demonstrator and includes the real operational helper code separately. Running and paused states, installed Docker CLI and reachable Linux engine, backup acceptance and inbox receipt are distinct observations. No additional SIEM routing or message is activated by these examples.

## Actual source and adaptations

Read [the source map](SOURCE-MAP.md) and [machine provenance](source-map.json) for every extracted implementation file.

## Dedicated recovery case study

The [backup and recovery project](https://github.com/truthofsource/azure-backup-and-recovery) goes deeper into key-version coverage, backup receipts, isolated recovery and data/file/state dependencies. Application artifact rollback and data recovery solve different problems.
