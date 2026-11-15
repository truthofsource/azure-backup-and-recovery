# Commands and expected results

**Terms used here:** A digest is a file or container fingerprint used to confirm the exact version. A managed identity lets an Azure service request access without storing a password in the application.

Run these commands **from this repository's root**, unless a step explicitly says otherwise. Commands in the proof sections are local reproductions of the included behavior, not live cloud operations.

## What was actually exercised

| Command group | Evidence status |
| --- | --- |
| Python suite and CLI demonstration | Executed locally; recorded in [validation results](validation-results.json) |
| Desktop/mobile workbench | Executed locally; screenshots and scope are in [validation](VALIDATION.md) |
| Terraform init, formatting, validate and mock plans | Passed; no cloud apply |
| Focused test selectors below | Reproduce included cases; no external account required |
| Source secret scan | One recorded Trivy scan covered all five prepared repositories; the recipe below is a per-repository equivalent |
| Optional container vulnerability/cloud/database procedure | Only claim execution when its own result is recorded; optional examples are labeled below |

Absolute local tool paths and temporary folder names are omitted so the examples are portable. Expected results explain what to check; they are not invented terminal transcripts. Recorded test counts and platform limits remain in the validation record.

## 1. Prepare Python

Requires Python 3.12 or newer. Bash / Linux / macOS / WSL:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

PowerShell alternative, without changing execution policy:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -B -m lab demo
```

Use the virtual environment's Python for later commands. The default demonstration requires no cloud sign-in or paid API request. Installing dependencies can download packages; it does not deploy infrastructure.

## 2. Run and inspect the reference

```bash
python -B -m unittest discover -s tests -v
python -B -m lab demo
python -B -m lab serve --port 8011
```

The suite should end in `OK`. A negative security case passes when the expected request is denied. The CLI prints JSON with `checks`, `metrics` and fictional `records`; each demonstration check should have `passed: true`. A failed assertion exits with an error.

The server command stays running. Open [the loopback workbench](http://127.0.0.1:8011), choose **Run demonstration**, then inspect **Validation** and **Evidence**. Stop with Ctrl+C. This serves a local interface; it does not publish a cloud application.

The focused commands beside [Proof It Works](../README.md#proof-it-works) run selected files/cases. `-p` selects a test file; `-k` selects matching test names. The entire suite above remains the broader check.

## 3. Validate Terraform without deploying

Use a Terraform version compatible with [the root's version constraint](../infra/versions.tf). Run from the repository root:

```bash
terraform -chdir=infra init -backend=false -input=false
terraform -chdir=infra fmt -check -recursive
terraform -chdir=infra validate
terraform -chdir=infra test
```

To select this project's mock plan file:

```bash
terraform -chdir=infra test -filter=tests/recovery.tftest.hcl
```

`init` downloads pinned providers and prepares the working directory; `-backend=false` does not adopt an organization's remote state. `fmt -check` checks formatting without rewriting files. `validate` checks configuration/schema, not deployment readiness. `test` uses the declared mock providers and plan commands, so the passing assertions are not Azure/Entra changes.

Keep the lock file in Git. Version repair during preparation used `init -upgrade` only to match an explicitly changed provider pin; do not routinely upgrade providers as a substitute for testing. No `terraform apply` or `destroy` is part of these reproduction steps.

## 4. Reproduce the source secret check

Requires Trivy. The recorded source scan used Trivy 0.75.0. This is the equivalent per-repository recipe, with local outputs excluded:

```bash
mkdir -p .local/security
trivy fs --scanners secret --skip-dirs .terraform --skip-dirs .venv --skip-dirs .local --format json --output .local/security/secrets.json .
```

In PowerShell, create the folder with `New-Item -ItemType Directory -Force .local/security` instead of `mkdir -p`. Review the JSON report and the tool's completion status; no output or a partial/error result is not a clean scan. Secret coverage is different from dependency, image or IaC findings. Keep reports local because findings can contain sensitive excerpts.

## 5. What the manual CI job runs

The [workflow](../.github/workflows/validate.yml) declares these shell steps after checkout and Python setup:

```bash
python -m pip install -r requirements.txt
python -B -m unittest discover -s tests -v
python -B -m lab demo
```

It has a manual trigger and no cloud identity/deployment permission. These docs do not dispatch it or spend Actions minutes. The Terraform mock checks are documented local steps, not a hidden additional CI job.

## PostgreSQL script checks

These syntax checks were performed for the public scripts. They do not run a database restore or upload a backup. Use Bash on Linux, macOS or WSL:

```bash
bash -n scripts/backup-postgres.sh
bash -n scripts/check-restore.sh
```

**Optional restore procedure, not executed for the public demonstration:** an approved dump, checksum, inventory and reviewed PostgreSQL 16 digest are required. Replace the placeholder first.

```bash
export PLATFORM_RESTORE_POSTGRES_IMAGE='postgres@sha256:<reviewed-digest>'
bash scripts/check-restore.sh dump.sql.gz dump.sql.gz.sha256 expected.inventory.json
```

That script creates a disposable network-isolated local container and removes it afterward. Follow [the PostgreSQL procedure](../scripts/README.md) for compatibility and consistency checks. The cloud-backup script uploads through managed identity and is a separate explicitly enabled operation; merely documenting it does not schedule or authorize a backup.


## Troubleshooting and cleanup

If imports fail, confirm that the command uses the virtual environment's Python. If port 8011 is occupied, choose an available port with `--port` and open the corresponding `127.0.0.1` URL. If Docker's CLI is installed but the engine is unreachable, start/check the Linux engine rather than reinstalling the application.

```bash
git status --short --ignored
git diff --check
```

Inspect owned local files before cleanup. `.venv`, `.local`, provider caches, state and saved plans are excluded from commits. Do not remove another checkout's files, paste credentials into a command block or run a real cloud apply just to reproduce a screenshot.

## Extracted implementation checks

Use Node 22.18+; no npm install is required for the default selected tests.

```bash
npm run test:source
```

These run original selected implementation tests with the adaptations listed in [SOURCE-MAP](SOURCE-MAP.md). No cloud operations are performed.
