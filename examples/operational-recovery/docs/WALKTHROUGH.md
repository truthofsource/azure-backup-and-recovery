# Implementation walkthrough

**Terms used here:** A digest is a file or container fingerprint used to confirm the exact version.

A small cloud platform needed reliable operational records, controlled running costs and a recovery path that did not depend on experimenting with its live database or exposing secret material.

## 1. Run the fast recovery demo

The code uses the database backup API, captures table counts and writes a checksum. It never overwrites an existing target.

## 2. Restore and compare

A separate target must pass integrity and row-count checks. The demo deliberately tests a corrupted archive and existing-target overwrite attempts.

## 3. Read the PostgreSQL procedure

The published shell scripts adapt the deployed platform approach: no-role-password dumps, managed-identity upload, a digest-pinned disposable database and no network. A successful empty server is not sufficient evidence.

## 4. Trace operational logs

Diagnostic settings route selected service categories to the operational workspace. KQL finds backup failures and delivery outcomes. Sentinel is an optional further ingestion decision, not an automatic destination for every table.

## Read the implementation

Start with [the domain module](../lab/domain.py), then [its tests](../tests/test_domain.py). The [dashboard report](../lab/demo.py) runs the same implementation; it does not substitute static success labels. `python -B -m lab demo` exits with an error if a demonstration assertion fails.

## Discuss the result

Describe the business problem first, the trust boundary second and the observed result third. Claim only the evidence in the validation record. A portable reference test is useful evidence of code behavior; it is not live-provider acceptance.

## Commands for this walkthrough

Start from the repository root. Run the working backup and recovery reference and its tests:

```bash
python -B -m unittest discover -s tests -v
python -B -m lab demo
```

Then follow the commands beside each [proof section](../README.md#proof-it-works). The [full command reference](COMMANDS.md) explains prerequisites, expected outcomes and which additional procedures have not been run.

## Follow the actual implementation

Read [the implemented path](IMPLEMENTATION.md), then [the selected source](../reference/) and original tests. The loopback workbench remains a portable local reference. It does not replay provider operations or prove a fresh hosted deployment.
