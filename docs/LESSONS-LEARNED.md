# Troubleshooting lessons from the actual platform

These are historical engineering incidents summarized from maintained internal records. They are not newly reproduced tests, a fresh cloud inventory or instructions to repeat a consumed operation. Names, resource identifiers, private payloads and credentials are excluded.

## A successful backup command produced no new backup

**What happened.** An operating command could finish successfully without a newly saved dump.

**What the evidence showed.** The backup service condition and helper could legitimately skip a stopped session. Command exit status alone therefore did not establish that a fresh backup had been created.

**What changed and how it was checked.** Acceptance required evidence that the stack was active and a new timestamped dump, checksum and inventory existed. The recorded procedure also checked the actual installed helper path and guest output instead of treating Azure Run Command delivery as guest-script completion.

**What to carry forward.** Distinguish success, intentional skip, fresh backup creation and verified restore. Preserve the timestamp and content evidence needed to tell them apart rather than labeling every zero exit status as a current backup.

Source record: `docs/troubleshooting/backstage-engineering-portal.md — Backup says success but no new object; Handbook helper path and Run Command output`. These internal paths identify provenance; they are not public file links.

## Related incident

[Backstage database-readiness incident](https://github.com/truthofsource/azure-backstage-developer-portal/blob/main/docs/LESSONS-LEARNED.md) explains the shared failure and verification. Its historical acceptance is not another hosted test performed for this repository.

## Evidence and project boundaries

The local examples and screenshots in this repository remain separate from the dated hosted incidents above. A new documentation summary does not establish another successful deployment, restore, security scan or business transaction. Follow the repository’s existing validation guide for the commands and limits of the runnable reference.

The practical sequence is: identify the failing boundary, preserve safe correlation evidence, reconcile any uncertain result, apply only the relevant repair and verify the resulting state. A completed local command is not interchangeable with a completed cloud operation.
