mock_provider "azurerm" {}
mock_provider "azapi" {}
variables {
  subscription_id      = "00000000-0000-0000-0000-000000000001"
  resource_group_name  = "rg-example-operations"
  storage_account_name = "stexamplebackups001"
}
run "retention_logging_and_no_compute" {
  command = plan
  assert {
    condition     = length(azurerm_linux_virtual_machine.recovery) == 0 && length(azurerm_role_assignment.backup_writer) == 0
    error_message = "VM and writer permission must stay opt-in."
  }
  assert {
    condition     = azurerm_log_analytics_workspace.operations.retention_in_days == 30 && azurerm_storage_account.data.blob_properties[0].versioning_enabled
    error_message = "Retain operational logs and versioned backup protection."
  }
  assert {
    condition     = azurerm_monitor_diagnostic_setting.backup_blob.log_analytics_destination_type == "Dedicated"
    error_message = "Storage logs must use the table mode expected by the example KQL."
  }
}

run "no_key_backup_access_by_default" {
  command = plan
  assert {
    condition     = length(azurerm_role_assignment.key_backup) == 0 && length(azurerm_role_definition.key_backup) == 0
    error_message = "Key backup access stays opt-in."
  }
}
run "backup_role_cannot_unwrap_or_delete" {
  command = plan
  variables {
    enable_key_backup_access = true
    source_key_arm_id        = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/rg-example/providers/Microsoft.KeyVault/vaults/kv-example/keys/wrapping-key"
    key_backup_principal_id  = "00000000-0000-4000-8000-000000000010"
  }
  assert {
    condition     = toset(azurerm_role_definition.key_backup[0].permissions[0].data_actions) == toset(["Microsoft.KeyVault/vaults/keys/read", "Microsoft.KeyVault/vaults/keys/backup/action"]) && azurerm_role_assignment.key_backup[0].scope == var.source_key_arm_id
    error_message = "Backup metadata/export permission must not become unwrap, rotation or deletion."
  }
}
