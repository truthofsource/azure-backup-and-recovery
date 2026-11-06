# Commands and expected results

**Terms used here:** A digest is a file or container fingerprint used to confirm the exact version. A managed identity lets an Azure service request access without storing a password in the application.

Use Python 3.12. Run from the repository root. No default command calls Azure.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -B -m unittest discover -s reference -v
python -B -m unittest discover -s tests -v
python -B -m lab demo
python -B -m lab serve --port 8011
```

PowerShell, without changing execution policy:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B -m unittest discover -s reference -v
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -B -m lab demo
.\.venv\Scripts\python.exe -B -m lab serve --port 8011
```

Expected: eleven source-recovery tests, successful portable tests and seven demonstration checks. The viewer listens on loopback and stops with Ctrl+C. The local demo contains no cloud HTTP client.

```bash
terraform -chdir=infra init -backend=false -input=false
terraform -chdir=infra fmt -check -recursive
terraform -chdir=infra validate
terraform -chdir=infra test
```

Expected: local schema validation and mock plans, no apply. Review [infra](../infra/README.md) before using real inputs.

On a Linux shell, syntax inspection of the operational helpers does not run a backup:

```bash
bash -n scripts/backup-postgres.sh scripts/check-restore.sh
```

The actual PostgreSQL helpers need Linux Docker, a reviewed digest-pinned PostgreSQL 16 image, a matching dump/checksum and preferably its inventory. The backup uploader additionally needs AzCopy and a separately commissioned container-specific managed identity. Do not execute it against a live host just to validate this portfolio.
