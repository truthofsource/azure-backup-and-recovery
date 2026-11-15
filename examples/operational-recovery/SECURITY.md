# Security and privacy

This is an educational reference derived from operational engineering patterns. Do not use the loopback dashboard as an internet-facing application.

- All displayed people and records are fictional. No tenant, subscription, private endpoint, employee ID or real document is required.
- The dashboard binds to `127.0.0.1`, checks Host and Origin, uses an explicit asset allowlist and sends a restrictive content security policy.
- State changes exposed by the dashboard rerun only test-only local fixtures. There is no cloud mutation endpoint.
- GitHub Actions has read-only repository permission, no OIDC token permission and a manual trigger. Dependencies/actions are pinned, but still require periodic review.
- Keep API keys, provider tokens, Terraform state, plans and real operational exports outside Git. Use managed identities and exact federated trust where possible.
- Local modeled policies and test-only scan receipts are not security attestations. Hosted adapters need provider-side authentication, least privilege and operational tests.

Report a defect through a GitHub issue using fictional reproduction data. Never attach credentials, private employee documents or real authentication traces.

## Extracted source boundary

Public example labels/identities are not valid production configuration. Selected original tests use fictional providers and cannot authorize a cloud operation. Read the source map before treating a helper as a complete deployable service. No state, keys, real backup payloads or employee records belong in this repository.
