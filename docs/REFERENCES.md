# Sources, adaptation and presentation credits

## Source of the engineering story

The architecture and operating lessons come from an Azure workforce/operations platform I built and operated. This public adaptation removes organization names, product branding, tenant/subscription/resource identifiers, private hostnames, employee records and secret material. Only curated reusable patterns are published; no private repository history is copied.

The loopback demonstration remains a local reference. Selected implementation source and original tests are now included separately, with each extraction/adaptation recorded in SOURCE-MAP.md. Screenshots show their actual local execution with synthetic fixtures. Cloud integration or historical acceptance is not inferred from those screenshots.

## Technical references

- [PostgreSQL pg_dumpall](https://www.postgresql.org/docs/current/app-pg-dumpall.html)
- [Azure Monitor diagnostic settings](https://learn.microsoft.com/en-us/azure/azure-monitor/platform/diagnostic-settings)
- [Log Analytics overview](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-overview)
- [Azure reliability](https://learn.microsoft.com/en-us/azure/reliability/)

## Presentation inspiration

- [Azure DevOps / AWS federation lab](https://github.com/Lia-Bing0/azure-devops-aws-federation-lab)
- [Multi-cloud IAM and NHI governance](https://github.com/JustinGallimore/multi-cloud-iam-nhi-governance)

These repositories informed the business-scenario, architecture, walkthrough and screenshot presentation. Their source code and screenshots were not copied. This project's code and assets are separately authored or adapted from my own platform material.

- [Network Security and Traffic Analysis](https://github.com/fabrizio-mastrogiovanni/Network-Security---Traffic-Analysis) — inspiration for the business-problem, solution, component-table and numbered-evidence presentation. Wording, implementation and screenshots in this project are its own.

## Recovery-specific references

- [Azure Key Vault protected backup and restore](https://learn.microsoft.com/en-us/azure/key-vault/general/backup)
- [Azure SQL point-in-time recovery](https://learn.microsoft.com/en-us/azure/azure-sql/database/recovery-using-backups?view=azuresql)
- [Azure Blob versioning](https://learn.microsoft.com/en-us/azure/storage/blobs/versioning-overview)
- [Terraform Azure backend](https://developer.hashicorp.com/terraform/language/backend/azurerm)
