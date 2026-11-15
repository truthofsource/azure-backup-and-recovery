# Adapted from the operational private-storage modules; neutral names only.
resource "azurerm_storage_account" "data" {
  name                              = var.storage_account_name
  resource_group_name               = azurerm_resource_group.lab.name
  location                          = var.location
  account_kind                      = "StorageV2"
  account_tier                      = "Standard"
  account_replication_type          = "LRS"
  min_tls_version                   = "TLS1_2"
  https_traffic_only_enabled        = true
  allow_nested_items_to_be_public   = false
  public_network_access_enabled     = false
  shared_access_key_enabled         = false
  default_to_oauth_authentication   = true
  cross_tenant_replication_enabled  = false
  infrastructure_encryption_enabled = true
  local_user_enabled                = false
  blob_properties {
    versioning_enabled = true
    delete_retention_policy { days = 30 }
    container_delete_retention_policy { days = 30 }
  }
  tags = var.tags
}
# Use the ARM child API so container creation does not require opening Blob ingress.
resource "azapi_resource" "containers" {
  for_each  = toset(["database-backups"])
  type      = "Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01"
  name      = each.value
  parent_id = "${azurerm_storage_account.data.id}/blobServices/default"
  body      = { properties = { publicAccess = "None" } }
}
output "storage_account_id" { value = azurerm_storage_account.data.id }
