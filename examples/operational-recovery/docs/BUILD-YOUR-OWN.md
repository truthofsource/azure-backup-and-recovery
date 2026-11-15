# Build your own from scratch: Platform Operations And Recovery

Your own small web service, private backup archive, isolated restore and measured recovery result.

Start with a new folder, your own files and your own accounts. The numbered steps below describe the build; no portfolio repository checkout is required. The existing implementation/evidence elsewhere in this repository is a separate reference, not a claim that your new build has already passed.

## Prerequisites

Docker with Linux containers, Bash/WSL, tar and a new disposable project folder. This exercises static application-data recovery; it is not a substitute for SQL transactional recovery or a whole-cloud disaster-recovery test.

Use Bash on Linux/macOS/WSL for Bash blocks and PowerShell for PowerShell blocks. Select the tool versions supported by the official sources below, record the versions you actually install and retain generated dependency locks. Cloud resources, scanner downloads, logs and external AI calls can create costs; review the stated scope before enabling them.

## Create your project folder

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

## Step 1 — Create data you can recognize after recovery

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

## Step 2 — Start your own service and record its image

**Where:** Your Docker host.

Set WEB_IMAGE to the entire reviewed RepoDigest value printed in the previous step, including the image name and @sha256: prefix exactly once. Run your service with the read-only data mount; a raw hexadecimal hash alone is not a runnable image reference.

```bash
export WEB_IMAGE="YOUR_COMPLETE_REVIEWED_NGINX_REPODIGEST_REFERENCE"
docker run -d --name my-recovery-web -p 127.0.0.1:8080:80   -v "$PWD/site:/usr/share/nginx/html:ro" "$WEB_IMAGE"
curl -fsS http://127.0.0.1:8080/
```

**Check before continuing:** The site returns your marker on loopback only.

## Step 3 — Create a private backup and manifest

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

## Step 4 — Restore into an empty separate folder

**Where:** Your own recovery folder.

Verify the backup hash before extraction and restore only your own trusted archive into a newly created directory. Keep the source service and files intact while proving the recovered copy.

```bash
sha256sum -c backups/site.tgz.sha256
mkdir restored-site
tar -xzf backups/site.tgz -C restored-site
cmp site/index.html restored-site/index.html
```

**Check before continuing:** The extracted file matches the source byte-for-byte.

## Step 5 — Start the recovered service separately

**Where:** Your Docker host.

Run a second container on another loopback port using the same selected image and restored data. Test the marker and record elapsed restore/start/verification time, not merely whether the container exists.

```bash
docker run -d --name my-restored-web -p 127.0.0.1:8081:80   -v "$PWD/restored-site:/usr/share/nginx/html:ro" "$WEB_IMAGE"
curl -fsS http://127.0.0.1:8081/
```

**Check before continuing:** The recovery URL serves the same marker while the original remains available.

## Step 6 — Document limits and clean up

**Where:** Your run record and terminal.

Record the backup time, selected image, hashes, restore timing and missing database/identity/network dependencies. Remove only the two lab containers and apply your own retention decision to the backup; do not represent this as a live enterprise restore.

```bash
docker rm -f my-recovery-web my-restored-web
```

**Check before continuing:** The restore has observable evidence and an honest scope.

## Verification and your own screenshots

| Evidence | What to record | Your result |
| --- | --- | --- |
| New build | Your own files/resource settings and tool versions | Not yet recorded |
| Working path | The actual successful request, configuration or recovery result | Not yet recorded |
| Failure boundary | A meaningful denied, malformed, stale or failed case | Not yet recorded |
| Recovery / cleanup | What you restored or removed and what remains billed | Not yet recorded |

Capture your own architecture/configuration, one working result and one failure/recovery result. Keep tokens, credentials, personal records and private identifiers out of public screenshots. The architecture diagram explains the design; record your own results rather than treating it as execution evidence.

## Troubleshooting order

1. Confirm the named file, working directory and selected tool/interpreter.
2. Check the exact input and resource/account selected for the failing step.
3. Separate identity permission, network/DNS reachability and application validation.
4. Keep the actual error and reconcile an unknown write outcome before repeating it; do not widen access or repeat paid operations blindly.

The numbered steps describe a build procedure. Local syntax checks, an accepted API request, a completed hosted operation and a human verification are different evidence levels; fill in the verification table with what you actually observed.

## Official implementation references

- [docs.docker.com — bind-mounts](https://docs.docker.com/engine/storage/bind-mounts/)
- [www.gnu.org — manual](https://www.gnu.org/software/tar/manual/)

The walkthrough layout follows the prerequisites → creation/configuration → test → verification → troubleshooting → cleanup pattern of the [Splunk project reference](https://github.com/davidharris6/splunk-siem-log-analysis). Its Splunk-specific settings are not copied into unrelated projects.
