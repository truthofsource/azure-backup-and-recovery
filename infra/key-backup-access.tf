variable "enable_key_backup_access" {
  type    = bool
  default = false
}
variable "source_key_arm_id" {
  type    = string
  default = ""
}
variable "key_backup_principal_id" {
  type    = string
  default = ""
}
resource "azurerm_role_definition" "key_backup" {
  count             = var.enable_key_backup_access ? 1 : 0
  name              = "example-key-backup-${var.storage_account_name}"
  scope             = "/subscriptions/${var.subscription_id}"
  assignable_scopes = ["/subscriptions/${var.subscription_id}"]
  permissions {
    data_actions = ["Microsoft.KeyVault/vaults/keys/read", "Microsoft.KeyVault/vaults/keys/backup/action"]
  }
}
resource "azurerm_role_assignment" "key_backup" {
  count              = var.enable_key_backup_access ? 1 : 0
  scope              = var.source_key_arm_id
  role_definition_id = azurerm_role_definition.key_backup[0].role_definition_resource_id
  principal_id       = var.key_backup_principal_id
  principal_type     = "ServicePrincipal"
  lifecycle {
    precondition {
      condition     = startswith(var.source_key_arm_id, "/subscriptions/${var.subscription_id}/resourceGroups/") && can(regex("/providers/Microsoft.KeyVault/vaults/[A-Za-z0-9-]+/keys/[A-Za-z0-9-]+$", var.source_key_arm_id)) && can(regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", var.key_backup_principal_id))
      error_message = "Review an exact key ARM scope in this subscription and the backup workload identity."
    }
  }
}
