# Troubleshooting lessons from the actual platform

These are historical engineering incidents summarized from maintained internal records. They are not newly reproduced tests, a fresh cloud inventory or instructions to repeat a consumed operation. Names, resource identifiers, private payloads and credentials are excluded.

## The investigation query missed the evidence

**What happened.** An initial historical recovery investigation found no matching completion outcome and could not explain why a code had not been submitted.

**What the evidence showed.** The logger appended a bounded status object to the message, so exact message equality missed real entries. Prefix matching later found no_candidate outcomes. Other historical queries also needed an explicit incident timespan rather than a default recent window.

**What changed and how it was checked.** The query was corrected to use the known prefix, exact UTC bounds and allowlisted outcome fields. This narrowed the diagnosis without copying message bodies, codes or tokens into the report or causing another provider sign-in.

**What to carry forward.** Validate query scope and log format before treating absence as proof that code never ran. Keep collection coverage, ingestion delay, query correctness and actual application behavior separate.

Source record: `docs/troubleshooting/carebridge-recovery.md — October 22 natural recovery observation and Safe mailbox-outcome query; docs/troubleshooting/layer-39h-b4-stage2-sensitive-data-commissioning-recovery.md — Historical telemetry queries`. These internal paths identify provenance; they are not public file links.

## Provider acceptance did not establish inbox receipt

**What happened.** The application recorded a provider-accepted Attendance email, but the intended recipient reported that it had not arrived.

**What the evidence showed.** The investigation separated the saved provider message ID, transport outcome and recipient observation. Bounced messages and nearby events had to be correlated to their exact records rather than assumed to explain every missing alert.

**What changed and how it was checked.** Read-only correlation used stored identifiers and transport evidence. A separately authorized generic test was later confirmed received; that demonstrated that test’s route, not retroactive delivery of the earlier Attendance alert.

**What to carry forward.** Show acceptance, delivery, bounce and user receipt as different observations. Do not automatically resend business alerts or attribute a missing email to a nearby bounce without exact correlation.

Source record: `docs/runbooks/production-workflow-observation-20261028.md; historical Attendance delivery investigation and authorized generic delivery test`. These internal paths identify provenance; they are not public file links.

## A child process consumed the rest of a remote script

**What happened.** Transfers completed, but later shell steps did not run during a remote maintenance operation.

**What the evidence showed.** A child process could consume stdin from a script supplied with bash -s. Successful command delivery and a completed transfer did not establish completion of the later phases.

**What changed and how it was checked.** The procedure executed the script from a file, redirected transfer stdin from /dev/null and required a final phase receipt. Guest output was checked separately from the Azure Run Command submission result.

**What to carry forward.** Define and verify an explicit completion signal for multi-step automation. Do not repeat a possibly completed write merely because a later reporting or shell-transport phase failed.

Source record: `docs/troubleshooting/vulnerability-scanning.md — Transfers complete but later shell steps never execute`. These internal paths identify provenance; they are not public file links.

## Evidence and project boundaries

The local examples and screenshots in this repository remain separate from the dated hosted incidents above. A new documentation summary does not establish another successful deployment, restore, security scan or business transaction. Follow the repository’s existing validation guide for the commands and limits of the runnable reference.

The practical sequence is: identify the failing boundary, preserve safe correlation evidence, reconcile any uncertain result, apply only the relevant repair and verify the resulting state. A completed local command is not interchangeable with a completed cloud operation.
