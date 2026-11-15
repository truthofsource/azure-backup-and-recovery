# Operations and troubleshooting

**Terms used here:** A digest is a file or container fingerprint used to confirm the exact version. An artifact is a file produced for a release, such as an application ZIP or container image.

## Start and stop

Run unit tests, then start the loopback dashboard with `python -B -m lab serve`. Stop with Ctrl+C. Each demonstration uses disposable test-only state; running it twice does not send messages or change a cloud resource.

## Diagnose by failure stage

| Symptom | Check and next action |
| --- | --- |
| Docker command works but Linux container fails | Separate CLI installation, engine reachability, selected context and Linux-engine support. Validate docker info before blaming the application. |
| Backup exists but restore fails | Check checksum, gzip integrity, PostgreSQL compatibility, roles and application database inventory. Preserve the failed receipt. |
| Expected log is missing | Check category, destination, table mode, time range, ingestion delay and caller permission. A diagnostic-setting resource does not prove arrival. |
| Delivery service accepted an email but user did not receive it | Correlate provider message ID and transport outcome. Acceptance, delivery, bounce and user receipt are different observations. |

## Cleanup

Default demos use managed temporary directories and close their own database handles. Do not run blanket recursive cleanup against a shared checkout. Inspect `git status --short --ignored`, stop the local server and remove only artifacts you created. Cloud resource cleanup is a separate reviewed operation and is never triggered by this repository's CI.

## Evidence to keep

Retain source commit, test command/exit status, tool versions and safe error stage. For a real release, also retain exact package/image digest and the restored operating state. Do not retain credentials, bearer tokens or employee data in public artifacts.
