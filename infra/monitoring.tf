resource "azurerm_log_analytics_workspace" "operations" {
  name                = var.workspace_name
  resource_group_name = azurerm_resource_group.lab.name
  location            = var.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}
resource "azurerm_monitor_diagnostic_setting" "backup_blob" {
  name                           = "diag-example-backup-blob"
  target_resource_id             = "${azurerm_storage_account.data.id}/blobServices/default"
  log_analytics_workspace_id     = azurerm_log_analytics_workspace.operations.id
  log_analytics_destination_type = "Dedicated"
  enabled_log { category = "StorageRead" }
  enabled_log { category = "StorageWrite" }
  enabled_log { category = "StorageDelete" }
}
resource "azurerm_role_assignment" "backup_writer" {
  count                = var.backup_writer_principal_id != "" ? 1 : 0
  scope                = azapi_resource.containers["database-backups"].id
  principal_id         = var.backup_writer_principal_id
  principal_type       = "ServicePrincipal"
  role_definition_name = "Storage Blob Data Contributor"
}
resource "azurerm_storage_management_policy" "backup_retention" {
  storage_account_id = azurerm_storage_account.data.id
  rule {
    name    = "expire-lab-database-backups"
    enabled = true
    filters {
      prefix_match = ["database-backups/"]
      blob_types   = ["blockBlob"]
    }
    actions {
      base_blob { delete_after_days_since_modification_greater_than = 90 }
      version { delete_after_days_since_creation = 30 }
    }
  }
}
output "workspace_id" { value = azurerm_log_analytics_workspace.operations.id }
