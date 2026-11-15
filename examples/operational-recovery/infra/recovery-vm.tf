# Optional private host shell. Creating a VM starts billable compute.
# No Backstage application, secret transfer or restore command is provisioned.
resource "azurerm_network_interface" "recovery" {
  count               = var.enable_recovery_vm ? 1 : 0
  name                = "nic-example-recovery"
  resource_group_name = azurerm_resource_group.lab.name
  location            = var.location
  ip_configuration {
    name                          = "private"
    subnet_id                     = var.recovery_subnet_id
    private_ip_address_allocation = "Dynamic"
  }
  tags = var.tags
}
resource "azurerm_linux_virtual_machine" "recovery" {
  count                           = var.enable_recovery_vm ? 1 : 0
  name                            = "vm-example-recovery"
  resource_group_name             = azurerm_resource_group.lab.name
  location                        = var.location
  size                            = var.vm_size
  network_interface_ids           = [azurerm_network_interface.recovery[0].id]
  admin_username                  = "laboperator"
  disable_password_authentication = true
  source_image_id                 = var.reviewed_vm_image_id
  secure_boot_enabled             = true
  vtpm_enabled                    = true
  admin_ssh_key {
    username   = "laboperator"
    public_key = var.ssh_public_key
  }
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
  }
  identity { type = "SystemAssigned" }
  lifecycle {
    precondition {
      condition     = var.reviewed_vm_image_id != "" && var.recovery_subnet_id != "" && startswith(var.ssh_public_key, "ssh-")
      error_message = "Provide a reviewed Gen2 image ID, private subnet and operator public SSH key before enabling recovery compute."
    }
  }
  tags = var.tags
}
