# Build your own from scratch: Azure Backup And Recovery

Your own Azure VM backup and an isolated restore, verified using a file you created before the backup.

Start with a new folder, your own files and your own accounts. The numbered steps below describe the build; no portfolio repository checkout is required. The existing implementation/evidence elsewhere in this repository is a separate reference, not a claim that your new build has already passed.

## Prerequisites

An isolated Azure VM you may back up, Azure Backup permissions, a separate restore VNet/subnet and a cost estimate for the vault, backup storage and temporary restored compute.

Use Bash on Linux/macOS/WSL for Bash blocks and PowerShell for PowerShell blocks. Select the tool versions supported by the official sources below, record the versions you actually install and retain generated dependency locks. Cloud resources, scanner downloads, logs and external AI calls can create costs; review the stated scope before enabling them.

## Create your project folder

Choose a new folder name. These first commands create a blank project; an optional `git init` gives it its own history. Create parent directories in your editor when a later step introduces a nested file.

```bash
mkdir my-azure-backup-and-recovery
cd my-azure-backup-and-recovery
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

## Step 1 — Prepare a recoverable workload

**Where:** Your own Linux VM through an approved administration path.

Write a unique harmless file on a persistent OS/data disk and record its hash, OS version and application dependencies. Do not use a temporary disk or /tmp for a backup marker.

```bash
sudo mkdir -p /var/lib/my-recovery-lab
printf 'My recovery marker\n' | sudo tee /var/lib/my-recovery-lab/marker.txt >/dev/null
sha256sum /var/lib/my-recovery-lab/marker.txt
```

**Check before continuing:** You have a file/hash pair that can be checked after restoring.

## Step 2 — Create the vault and protection policy

**Where:** Azure Portal → Recovery Services vaults → Create.

Create a vault in the appropriate region for your VM and set its redundancy, security and retention choices. Select Backup → Azure → Virtual machine, choose a policy and add only your lab VM.

**Check before continuing:** The vault lists the VM as a protected item under your chosen policy.

## Step 3 — Run and verify a backup

**Where:** Vault → Backup items → Azure Virtual Machine.

Start Backup now and follow the job to its terminal result. Record the actual recovery point and any application-consistency limitations instead of treating submission as completion.

**Check before continuing:** A completed backup job and selectable recovery point exist.

## Step 4 — Restore separately

**Where:** Protected VM → Restore VM.

Select that recovery point and Create new virtual machine into the isolated restore network. Use a new name, avoid attaching it to the source application, and account for the staging storage/identity prerequisites shown by the restore wizard.

**Check before continuing:** A distinct restored VM exists without replacing the original.

## Step 5 — Prove recovery

**Where:** Your approved administration path on the restored VM.

Verify its resource/VM identity before reading the marker and comparing the hash. Check application start, storage mounts and required access separately; a successful boot does not prove the application is usable.

**Check before continuing:** The restored marker matches and every additional readiness check has an observed result.

## Step 6 — Close the rehearsal

**Where:** Your evidence record and vault.

Record backup/restore timing, RPO/RTO observations and missing dependencies. Remove only the temporary restore resources, then deliberately choose how the lab protected item and retained backup data should be handled; never disable a shared vault lock or purge recovery data as routine cleanup.

**Check before continuing:** The run is documented and all temporary compute/storage costs have an owner.

## Verification and your own screenshots

| Evidence | What to record | Your result |
| --- | --- | --- |
| New build | Your own files/resource settings and tool versions | Not yet recorded |
| Working path | The actual successful request, configuration or recovery result | Not yet recorded |
| Failure boundary | A meaningful denied, malformed, stale or failed case | Not yet recorded |
| Recovery / cleanup | What you restored or removed and what remains billed | Not yet recorded |

Capture your own architecture/configuration, one working result and one failure/recovery result. Keep tokens, credentials, personal records and private identifiers out of public screenshots. Existing portfolio images are references, not evidence that you performed these steps.

## Troubleshooting order

1. Confirm the named file, working directory and selected tool/interpreter.
2. Check the exact input and resource/account selected for the failing step.
3. Separate identity permission, network/DNS reachability and application validation.
4. Keep the actual error and reconcile an unknown write outcome before repeating it; do not widen access or repeat paid operations blindly.

The numbered steps describe a build procedure. Local syntax checks, an accepted API request, a completed hosted operation and a human verification are different evidence levels; fill in the verification table with what you actually observed.

## Official implementation references

- [learn.microsoft.com — backup-azure-vms-first-look-arm](https://learn.microsoft.com/en-us/azure/backup/backup-azure-vms-first-look-arm)
- [learn.microsoft.com — backup-azure-arm-restore-vms](https://learn.microsoft.com/en-us/azure/backup/backup-azure-arm-restore-vms)

The walkthrough layout follows the prerequisites → creation/configuration → test → verification → troubleshooting → cleanup pattern of the [Splunk project reference](https://github.com/davidharris6/splunk-siem-log-analysis). Its Splunk-specific settings are not copied into unrelated projects.
