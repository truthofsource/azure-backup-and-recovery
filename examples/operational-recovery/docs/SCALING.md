# Scaling, strengths and tradeoffs

## When the workload grows

Define recovery tiers by business impact and test RPO/RTO against actual service objectives. Use isolated accounts/subscriptions for drills, immutable backup retention where required and key-version retention for encrypted backups. At higher volume partition logs by purpose, redact before ingestion, monitor sampling gaps and alert on backup age. Tags and budgets improve cost ownership, but budget alerts are not hard spending caps.

## Design choices

| Choice | Strength, weakness and tradeoff |
| --- | --- |
| Isolated restore | Proves more than a successful upload and protects the live target. Requires temporary compute, a reviewed image and application-level verification. |
| Count inventory | Detects missing databases/tables/rows without exposing record values. Equal counts alone do not establish semantic correctness or transaction consistency. |
| Central logging | Improves troubleshooting across services. Ingestion, retention and sensitive fields need explicit ownership and cost review. |
| Paused nonproduction | Reduces compute spending and unintended work. Pending scans and dormant schedules require clear operator communication; storage charges can remain. |

## Operating measures

Measure throughput, oldest pending work, duplicate/rejected operations, failure stage and recovery duration. Tie alerts to an operator action. Do not infer service availability from an old successful import or infer delivery from provider acceptance.

Start with measured load and an explicit service objective. Increase concurrency only after checking provider quotas, database contention, per-person ordering and recovery behavior. Horizontal scaling requires a shared durable store; independent in-memory or SQLite processes are not a distributed coordination system.
