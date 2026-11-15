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
