# Terraform infrastructure

An operational Log Analytics workspace, private backup storage, scoped optional backup-writer access, Blob audit routing/retention and an optional private Linux recovery-host shell.

These configurations adapt the same resource boundaries used in the author's workforce/operations platform. Names and input examples are neutral; no environment state, backend, import block, secret or production identifier is included. Each folder is a standalone reference root, not a command to adopt an existing production resource into new state.

## Code map

| File | Purpose |
| --- | --- |
| [monitoring.tf](monitoring.tf) | 30-day operational workspace, dedicated StorageBlobLogs routing, container-specific writer grant and backup lifecycle policy. |
| [storage.tf](storage.tf) | Private keyless versioned backup account and ARM container declaration. |
| [recovery-vm.tf](recovery-vm.tf) | Opt-in private-NIC Linux VM, SSH keys, managed identity and Gen2 secure-boot requirements; no public IP. |
| [tests/recovery.tftest.hcl](tests/recovery.tftest.hcl) | No VM/grant by default; retention, versioning and table-mode checks. |
| [versions.tf](versions.tf) | Exact provider versions; lock file records provider checksums. |
| [example inputs](example.tfvars.example) | Reviewable inputs with placeholders; never actual tenant values. |

## Validate locally without a cloud deployment

```bash
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
terraform test
```

The `.tftest.hcl` files use mock providers and plan commands. They do not authenticate to Azure, create resources or mutate Entra. Provider initialization downloads provider packages; it is not an infrastructure deployment. No automatic Terraform apply is included in GitHub Actions. The existing workflow remains manual-only to avoid unnecessary Actions usage.

The `.tfvars.example` file is not loaded automatically. It contains placeholders and is not ready for a real plan. Leave real `.tfvars`, backend/state, saved plans and credentials outside Git. If you separately deploy a lab, review exact subscription/tenant, names, complete saved plan, permissions, network route, costs and cleanup first. Use a protected remote backend with Entra authentication; this public root deliberately supplies no organization backend.

## Integration boundaries

The VNet/subnet, private access route, approved compatible Gen2 image, SSH public key, portal package/TLS, secret material and backup schedule are separate. The root creates no backup, runs no restore and does not install the engineering portal. A VM needs a reviewed management route/NSG; this example does not open SSH to the internet.

## Security and activation

The optional VM and backup-writer grant remain off. Enabling a VM starts billable compute; no automatic deallocation timer is declared. The destination alone is not a backup acceptance result. Blob audit categories use Dedicated mode to match the StorageBlobLogs example KQL. No Sentinel workspace onboarding or extra SIEM ingestion is configured.

## Cost, retention and cleanup

Log ingestion, retained backups, disks and any enabled recovery VM can be billed. A deallocated VM can still incur storage costs. The sample 90-day base-blob/30-day version expiry is a lab policy, not an assumed organization retention requirement; soft deletion can extend retained billed data after lifecycle deletion.

Mock-test cleanup is entirely local. A real destroy is a separate reviewed action against the correct lab state; never run it against copied production state or shared resources. Payroll deletion protection in the identity example intentionally prevents a casual destroy of that group. Retire grants/trust and inventory retained recovery artifacts before removing a real lab.

## Strengths and tradeoffs

Central operational logs simplify investigations but need redaction, arrival checks and cost ownership. Isolated restore hosts protect the live application but require image compatibility, access, recovery material and explicit shutdown/cleanup.

## Resource inventory

| Terraform resource type | Local name | Definition |
| --- | --- | --- |
| `azurerm_resource_group` | `lab` | [main.tf](main.tf) |
| `azurerm_log_analytics_workspace` | `operations` | [monitoring.tf](monitoring.tf) |
| `azurerm_monitor_diagnostic_setting` | `backup_blob` | [monitoring.tf](monitoring.tf) |
| `azurerm_role_assignment` | `backup_writer` | [monitoring.tf](monitoring.tf) |
| `azurerm_storage_management_policy` | `backup_retention` | [monitoring.tf](monitoring.tf) |
| `azurerm_network_interface` | `recovery` | [recovery-vm.tf](recovery-vm.tf) |
| `azurerm_linux_virtual_machine` | `recovery` | [recovery-vm.tf](recovery-vm.tf) |
| `azurerm_storage_account` | `data` | [storage.tf](storage.tf) |
| `azapi_resource` | `containers` | [storage.tf](storage.tf) |

## Official references

- [Terraform test command and mock providers](https://developer.hashicorp.com/terraform/cli/commands/test)
- [AzureRM provider documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Registry repository permissions](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-rbac-abac-repository-permissions)

See [project architecture](../docs/ARCHITECTURE.md) and [validation evidence](../docs/VALIDATION.md) for the separate application/reference boundaries.

## Actual key-backup permission boundary

`key-backup-access.tf` adapts the implemented source-key metadata/backup custom role. It is Off by default. When separately reviewed, the assignment targets an exact key ARM scope; data actions exclude unwrap, rotation, deletion and restore. The role definition's assignable scope is subscription-level, while the grant itself is key-scoped. Mock tests inspect this distinction.

The root does not deploy the real private Container Apps schedule or restore workflow. Source backing: the platform recovery automation and VM backup Terraform. Retention values in this portable root are examples, not a declaration that every production store has identical retention.
