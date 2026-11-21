> This example is maintained within **azure-backup-and-recovery**. Run its local commands from this subfolder; its nested workflow files are retained examples and are not active repository workflows. See [the consolidation guide](https://github.com/truthofsource/azure-backup-and-recovery/blob/main/docs/CONSOLIDATION.md).

# Platform Operations & Recovery Engineering

**Test recovery, make logs useful and keep temporary cloud resources under control.**

[The problem](#the-business-problem) · [The solution](#the-solution) · [What was built](#what-was-built) · [Proof it works](#proof-it-works) · [Run it](#run-it-locally) · [Step by step](#step-by-step)

## The Business Problem

When a service fails, the operator needs to establish what stopped, which records or imports were affected and whether the last operation actually completed. Information spread across job histories, application logs and cloud settings makes that investigation slower and can encourage repeating an action whose outcome is still uncertain.

Recovery adds practical dependencies: a backup must be readable, the restored service needs its configuration and permissions, and testing must leave the live system intact. Temporary recovery hosts and diagnostic services can continue charging after the investigation ends. A successful backup job alone answers only part of the recovery question.

The business need was a repeatable operating process for diagnosis, isolated recovery checks and verified cleanup, so the next operator has usable evidence and clear actions during an incident.

## The Solution

Save backups and a record of what they contain, restore them into a separate test environment, and compare the results. Define where logs go and how staff use them to investigate failures. Stop temporary services and confirm their final state after testing.

**Business outcome:** Make recovery repeatable, operating information clearer and temporary-resource cleanup easier to verify.

### Platform implementation

- Operated a Linux-hosted engineering portal with access based on verified sign-in, private runtime material, backups and a tested temporary recovery-host procedure.
- Implemented checksum-verified PostgreSQL backups and restore checks in a separate disposable test environment, with database/table/row-count inventory comparison.
- Documented application and infrastructure logs, service diagnostics, Log Analytics queries and the difference between provider acceptance and actual delivery.
- Preserved paused nonproduction states after bounded tests and tracked residual costs, resource ownership and backup/retention requirements.

This case study draws on a workforce/operations platform I designed and implemented. Organization details and records are excluded. The public code makes selected patterns reproducible; the local demonstration uses fictional data, and its placeholder screenshots have been removed. [Validation scope](docs/VALIDATION.md) separates that evidence from testing against the actual cloud service.

### Actual implementation code

This repository now includes selected implementation source and original tests from the operational platform, rather than only a portable reference. Read [what was implemented and accepted](docs/IMPLEMENTATION.md), [the source map](docs/SOURCE-MAP.md) and the dated validation boundaries. Identifying configuration is replaced with examples; original private history and records are excluded.

## Tools Used and What They Do

| Tool or service | What it does | Where it fits |
| --- | --- | --- |
| Application Insights and Log Analytics | Collect application/runtime and operational log evidence. | Actual platform destinations; configuration alone does not establish ingestion. |
| KQL | Query logs by the relevant time, workload and safe correlation fields. | Query language, not a separate collector or proof of a complete incident history. |
| Azure CLI and PowerShell | Inspect achieved service state and support scoped operations. | Operating utilities; local command success is not every remote step completing. |
| PostgreSQL tools, Docker and AzCopy | Support engineering-portal database backup and transfer. | Actual helper prerequisites; separate from the SQLite teaching exercise. |
| Python and SQLite | Run the isolated recovery model and reference viewer. | Public local tools, not the production database engine. |
| Terraform and GitHub Actions | Describe infrastructure and coordinate reviewed checks. | Public checks are manual-only and do not start cloud services. |

Provider acceptance, transport delivery and inbox receipt remain different observations. The reference does not add a new Sentinel connector or logging pipeline.

## Step by Step

Your own small web service, private backup archive, isolated restore and measured recovery result.

[Open the standalone build guide](docs/BUILD-YOUR-OWN.md) or follow the same complete instructions below.

Start with a new folder, your own files and your own accounts. The numbered steps below describe the build; no portfolio repository checkout is required. The existing implementation/evidence elsewhere in this repository is a separate reference, not a claim that your new build has already passed.

### Prerequisites

Docker with Linux containers, Bash/WSL, tar and a new disposable project folder. This exercises static application-data recovery; it is not a substitute for SQL transactional recovery or a whole-cloud disaster-recovery test.

Use Bash on Linux/macOS/WSL for Bash blocks and PowerShell for PowerShell blocks. Select the tool versions supported by the official sources below, record the versions you actually install and retain generated dependency locks. Cloud resources, scanner downloads, logs and external AI calls can create costs; review the stated scope before enabling them.

### Create your project folder

Choose a new folder name. These first commands create a blank project; an optional `git init` gives it its own history. Create parent directories in your editor when a later step introduces a nested file.

```bash
mkdir my-platform-operations-and-recovery
cd my-platform-operations-and-recovery
git init
```

Create `.gitignore` before saving credentials or build outputs:

```gitignore
.venv/
node_modules/
.env
.env.*
local.settings.json
credentials.json
token.json
*.pem
*.key
*.tfstate*
*.tfplan
.terraform/
private*/
captures/
backups/
batch.json
reports/
out/
app-config.local.yaml
```

The source/file snippets are a starting implementation you type or paste into the named files. Replace `YOUR_*`, names, regions and addresses only with values from your own lab; do not place real client/employee records in a test project. Keep your terminal in this project root unless a step explicitly changes directory.

Before a first commit, set your own repository-local author with `git config user.name "YOUR_NAME"` and `git config user.email "YOUR_PUBLIC_COMMIT_EMAIL"`. Review `git status --short` and the staged diff before publishing; ignored local files are not a substitute for reviewing what you upload.

### Step 1 — Create data you can recognize after recovery

**Where:** Your new site folder.

Create site/index.html with the unique marker below. Decide which files are data, configuration, secret material and rebuildable binaries before choosing a backup scope.

Create **`site/index.html`** with the following contents:

```html
<!doctype html><html lang="en"><title>My recovery lab</title><h1>Recovery marker LAB-001</h1></html>
```

To select a base image, pull your reviewed tag and record its digest before replacing the digest placeholder. A changing tag is not an immutable release record.

```bash
docker pull nginx:stable
docker image inspect nginx:stable --format '{{index .RepoDigests 0}}'
```

**Check before continuing:** The test content is distinguishable from an empty default site.

### Step 2 — Start your own service and record its image

**Where:** Your Docker host.

Set WEB_IMAGE to the entire reviewed RepoDigest value printed in the previous step, including the image name and @sha256: prefix exactly once. Run your service with the read-only data mount; a raw hexadecimal hash alone is not a runnable image reference.

```bash
export WEB_IMAGE="YOUR_COMPLETE_REVIEWED_NGINX_REPODIGEST_REFERENCE"
docker run -d --name my-recovery-web -p 127.0.0.1:8080:80   -v "$PWD/site:/usr/share/nginx/html:ro" "$WEB_IMAGE"
curl -fsS http://127.0.0.1:8080/
```

**Check before continuing:** The site returns your marker on loopback only.

### Step 3 — Create a private backup and manifest

**Where:** Your project folder.

Use a private backup directory, archive only this known site folder and record a hash. For a changing database, use its database-aware backup/quiescing procedure; this static archive is not such a procedure.

```bash
umask 077
mkdir -p backups
tar -czf backups/site.tgz -C site .
sha256sum backups/site.tgz > backups/site.tgz.sha256
sha256sum site/index.html > backups/source-file.sha256
```

**Check before continuing:** You have an archive and a digest identifying the exact backup.

### Step 4 — Restore into an empty separate folder

**Where:** Your own recovery folder.

Verify the backup hash before extraction and restore only your own trusted archive into a newly created directory. Keep the source service and files intact while proving the recovered copy.

```bash
sha256sum -c backups/site.tgz.sha256
mkdir restored-site
tar -xzf backups/site.tgz -C restored-site
cmp site/index.html restored-site/index.html
```

**Check before continuing:** The extracted file matches the source byte-for-byte.

### Step 5 — Start the recovered service separately

**Where:** Your Docker host.

Run a second container on another loopback port using the same selected image and restored data. Test the marker and record elapsed restore/start/verification time, not merely whether the container exists.

```bash
docker run -d --name my-restored-web -p 127.0.0.1:8081:80   -v "$PWD/restored-site:/usr/share/nginx/html:ro" "$WEB_IMAGE"
curl -fsS http://127.0.0.1:8081/
```

**Check before continuing:** The recovery URL serves the same marker while the original remains available.

### Step 6 — Document limits and clean up

**Where:** Your run record and terminal.

Record the backup time, selected image, hashes, restore timing and missing database/identity/network dependencies. Remove only the two lab containers and apply your own retention decision to the backup; do not represent this as a live enterprise restore.

```bash
docker rm -f my-recovery-web my-restored-web
```

**Check before continuing:** The restore has observable evidence and an honest scope.

### Verification and your own screenshots

| Evidence | What to record | Your result |
| --- | --- | --- |
| New build | Your own files/resource settings and tool versions | Not yet recorded |
| Working path | The actual successful request, configuration or recovery result | Not yet recorded |
| Failure boundary | A meaningful denied, malformed, stale or failed case | Not yet recorded |
| Recovery / cleanup | What you restored or removed and what remains billed | Not yet recorded |

Capture your own architecture/configuration, one working result and one failure/recovery result. Keep tokens, credentials, personal records and private identifiers out of public screenshots. The architecture diagram explains the design; record your own results rather than treating it as execution evidence.

### Troubleshooting order

1. Confirm the named file, working directory and selected tool/interpreter.
2. Check the exact input and resource/account selected for the failing step.
3. Separate identity permission, network/DNS reachability and application validation.
4. Keep the actual error and reconcile an unknown write outcome before repeating it; do not widen access or repeat paid operations blindly.

The numbered steps describe a build procedure. Local syntax checks, an accepted API request, a completed hosted operation and a human verification are different evidence levels; fill in the verification table with what you actually observed.

### Official implementation references

- [docs.docker.com — bind-mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [www.gnu.org — manual](https://www.gnu.org/software/tar/manual/)

<details>
<summary>Reference: how the existing platform implementation operates</summary>

A short walkthrough of the process, with technical instructions and evidence limits in the sections below.

1. **Collect operating evidence (Log Analytics and KQL)** — Save useful service logs, delivery information and backup records. Keep provider acceptance separate from confirmed message delivery.

2. **Prepare a recovery copy** — Identify the records and configuration required for the selected system. Use backups with content checks and a separately owned destination.

3. **Compare the recovered result** — Check the restored contents and the access needed to use them. The case study keeps local demonstrations separate from completed live operating evidence.

4. **Close the temporary session** — Record the result and restore the intended service settings. Remove or pause temporary resources and note costs that continue after compute stops.

</details>

## Architecture

1. **Operational application** → **Database**.
2. **Database** → **Backup and count inventory**.
3. **Backup and count inventory** → **Private versioned backup storage**.
4. **Private versioned backup storage** → **Checksum and archive verification**.
5. **Checksum and archive verification** → **Disposable isolated restore**.
6. **Disposable isolated restore** → **Application inventory comparison**.
7. **Apps / jobs / storage** → **Diagnostic settings**.
8. **Diagnostic settings** → **Log Analytics workspace**.
9. Log Analytics workspace has a conditional/reference connection to Optional SIEM ingestion (selected approved tables).

[View the illustrated project overview](../../docs/diagrams/architecture.svg).

## What Was Built

| Component | Role in plain words | Implementation |
| --- | --- | --- |
| Actual delivery-status correlation | Match provider, recipient and time without confusing acceptance with delivery | [Reader](reference/deliveryReports.ts) · [original tests](reference/deliveryReports.test.ts) |
| Local recovery reference | Back up a fictional database and restore it into a different exclusive target. | [View code](lab/domain.py) |
| PostgreSQL backup/restore scripts | Save a file fingerprint and contents list, then practise recovery with the test network disconnected. | [View code](scripts) |
| Private backup storage | Use keyless access, versioning and deletion protection. | [View code](infra/storage.tf) |
| Log Analytics and Blob diagnostics | Route audit categories into dedicated storage tables with 30-day operational retention. | [View code](infra/monitoring.tf) |
| Backup lifecycle and optional writer role | Make retention and container-specific access reviewable in code. | [View code](infra/monitoring.tf) |
| Optional recovery-host shell | Define a private-NIC Linux VM with SSH keys; it remains unprovisioned by default. | [View code](infra/recovery-vm.tf) |
| Operational queries | Provide KQL starting points for backup traces and storage authentication. | [View code](queries/operations.kql) |

## Recovery Evidence in Sentinel

Selected existing recovery and storage observations now reach the hub security workspace through a separate metadata-only collector. This adds investigation context; it does not turn a backup receipt into proof of restoration or activate new operations alerts.

[Evidence, boundaries and the companion Sentinel implementation](docs/SECURITY-OBSERVABILITY.md) explains what was verified. The local demonstration below retains its fictional scope.

## Proof It Works

### Extracted platform code

```bash
npm run test:source
```

The selected original tests run offline. [Validation](docs/VALIDATION.md) records current counts and distinguishes them from historical hosted evidence.

**Current local checks:** 12 extracted-source tests + 10 portable tests passed · 5 demonstration checks · 1 Terraform tests using simulated cloud responses.

These are dated results for this reference implementation, not live Azure/AWS deployment claims. [Test record](docs/validation-results.json) · [Evidence and limitations](docs/VALIDATION.md)

### 1. A separate restore matches the saved inventory

The local SQLite rehearsal checks database integrity and compares table/row counts against the source snapshot.

Run from the repository root:

```bash
python -B -m unittest discover -s tests -p test_domain.py -v
```

**What to look for:** The local restore passes integrity and row-count checks using an isolated target.

### 2. Unsafe restore attempts are blocked

A corrupt archive is rejected before creating a target. Existing-target and self-restore attempts cannot overwrite the live database or backup.

Run from the repository root:

```bash
python -B -m unittest discover -s tests -p test_domain.py -k no_ -v
```

**What to look for:** The selected cases reject overwrite/self-restore attempts without modifying the live database.

### 3. Infrastructure defaults are verified

Mock plans keep the recovery VM and writer grant absent by default, and verify versioning, workspace retention and dedicated storage-log table mode. PostgreSQL scripts received syntax checks; these screenshots do not claim a live PostgreSQL/cloud restore.

Run from the repository root:

```bash
terraform -chdir=infra test -filter=tests/recovery.tftest.hcl
```

**What to look for:** The mock plan verifies no recovery VM/writer grant by default, storage protection and dedicated log-table routing.

### 4. Visible results

The dashboard runs the same domain code as the CLI. Desktop/mobile rendering, all three tabs, rerunning the demonstration, cross-origin write rejection and unlisted-file rejection were checked. Those local test results remain documented; proper application screenshots are deferred.

Expected access denials are successful negative tests. Cloud permissions, network connectivity and provider integrations need their own acceptance evidence.

## Security Practices

- The default rehearsal uses fictional local data and a separate target. A checksum proves consistency only when its saved value comes from trusted evidence.
- The optional VM has no public IP and needs a separately reviewed private management route. Enabling it starts billable compute.
- The monitoring root adds operational workspace routing, not Sentinel onboarding or a backup schedule. Log arrival and restore success remain separate observations.

State, saved Terraform plans, private inputs and credentials are excluded through [`.gitignore`](.gitignore). The existing validation workflow is manual-only and has no cloud deployment permission.

## Run It Locally

The [command reference](docs/COMMANDS.md) includes prerequisites, Windows equivalents, focused checks and evidence notes.

Requires Python 3.12 or newer. The default demonstration uses the Python standard library. Run inside a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -B -m unittest discover -s tests -v
python -B -m lab demo
python -B -m lab serve --port 8011
```

On Windows, use `.venv\Scripts\Activate.ps1` instead of the `source` command, or run `.venv\Scripts\python.exe` directly. Open [the local workbench](http://127.0.0.1:8011), choose **Run demonstration**, then review **Validation** and **Evidence**. Stop with Ctrl+C. No cloud login, employee data or paid API request is required.

## Terraform Infrastructure

An operational Log Analytics workspace, private backup storage, scoped optional backup-writer access, Blob audit routing/retention and an optional private Linux recovery-host shell.

See the [Terraform code and validation steps](infra/README.md), [input example](infra/example.tfvars.example) and [mock plan tests](infra/tests). Cloud commissioning and any paid resources remain separate from the local demonstration.

Validate the infrastructure source without creating cloud resources:

```bash
cd infra
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
terraform test
```

The tests use mock providers. Example inputs are placeholders, not deployment-ready values. Review the [integration boundaries and cost notes](infra/README.md) before any separate cloud commissioning.

## Scaling and Tradeoffs

Assign recovery tiers by business impact, then measure real RPO/RTO against those objectives. Protect encryption-key versions, test isolated recovery and track log ingestion, retention costs and backup age as the platform grows.

See [strengths, weaknesses and tradeoffs](docs/SCALING.md) for the detailed decisions.

## Skills Demonstrated

- Linux and container operations
- Backup integrity and isolated recovery
- Azure Monitor, Log Analytics and KQL
- Storage retention and managed-identity access
- Operational evidence and cloud cost control

## Troubleshooting Lessons

An investigation query initially missed real recovery outcomes, and provider acceptance did not establish inbox receipt. Both cases required checking the evidence path before repeating a business operation. [Read the incident, evidence and verification](docs/LESSONS-LEARNED.md).

## Project Guides

| Guide | What you will find |
| --- | --- |
| [Command reference](docs/COMMANDS.md) | Copy the commands, understand their purpose and check expected results |
| [Implementation walkthrough](docs/WALKTHROUGH.md) | Follow the processing path and code |
| [Architecture](docs/ARCHITECTURE.md) | Understand service and identity boundaries |
| [Terraform](infra/README.md) | Read the resource map, input examples and integration steps |
| [Validation evidence](docs/VALIDATION.md) | See the test dates, results and limits |
| [Operations and troubleshooting](docs/OPERATIONS.md) | Diagnose failures and recover safely |
| [Security and privacy](SECURITY.md) | Review access, secrets and publication controls |
| [Scaling and tradeoffs](docs/SCALING.md) | Understand the costs of each design choice |
| [References](docs/REFERENCES.md) | See technical sources and presentation inspiration |

## Repository Map

`reference/` contains extracted implementation logic and original selected tests.

```text
infra/               Terraform source, example inputs and mock plan tests
lab/                 Working reference implementation and loopback dashboard
tests/               Positive, negative and recovery cases
docs/                Architecture, walkthrough, evidence and operating guide
.github/workflows/   Manual-only contract validation; no cloud deployment
```

## Cost and Cleanup

The default local demo creates only temporary local state and makes no paid calls. Cloud examples are separate opt-in source and can create billable resources if an operator applies them. No automated deployment or destruction is configured. Use `git status --short --ignored` before cleanup; remove only your own `.venv` or disposable lab output. Never copy real state files, tokens or employee documents into this repository.
