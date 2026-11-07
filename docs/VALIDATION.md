# Validation evidence — November 6, 2026

**Terms used here:** A fixture is test data or a test setup used instead of real business records.

## Executed locally for this revision

| Check | Result |
| --- | --- |
| Extracted implementation tests | 11 passed; Python 3.12 |
| Portable/reference Python tests | 11 passed |
| Demonstration assertions | 7 passed |
| Terraform schema / mock plans | Valid; 3 passed; no apply |
| Desktop/mobile UI | Passed, 390 px mobile; no horizontal overflow or runtime errors |
| Loopback boundaries | External-Origin write rejected; unlisted asset rejected |
| Workflow syntax | actionlint 1.7.12 passed; manual-only; no hosted run |
| Selected-source secret scan | Trivy 0.75.0: zero findings |

The [machine record](validation-results.json) contains source hashes and date. Images come from actual local workbench runs with fictional records.

## Source and fixture boundaries

Read [SOURCE-MAP](SOURCE-MAP.md). Original selected tests remain distinct from new public fixture tests and the earlier portable demonstration. No Azure identity, permission, network path, provider action or current production recovery was exercised. The secret scan does not establish that every dependency/container is vulnerability-free. No new cloud resource, paid operation or Actions run was used.

Historical implementation/acceptance descriptions are source-runbook summaries, not new receipts. PostgreSQL scripts are actual operational helpers; only source inspection and mocked inventory behavior were checked here. No current PostgreSQL restore is claimed. The backup project's fake wrap/unwrap is not cryptographic acceptance.

## Reproduce

Use [the command reference](COMMANDS.md), then inspect expected positive and negative cases. Cloud commissioning, live restores, exact release authorization and trusted scanner/signature evidence remain separate from these offline fixtures.

## Troubleshooting documentation review — November 7, 2026

Added a README incident summary and a linked historical lessons guide, checking the account against the maintained source records. Documentation checks covered local links, complete incident fields, identifying-information patterns, whitespace and preservation of the existing four-step walkthrough. Shared incidents link to the relevant project details; unresolved causes remain explicit.

This was an editorial update. Application code, tests, Terraform, images, workflow definitions and cloud settings were not changed. Existing functional test counts and screenshots above retain their original scope and dates; no application suite, live scan, paid image request, recovery rehearsal or GitHub Actions run was executed for this documentation pass.
