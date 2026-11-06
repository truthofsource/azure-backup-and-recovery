variable "subscription_id" { type = string }
variable "location" {
  type    = string
  default = "eastus2"
}
variable "resource_group_name" { type = string }
variable "tags" {
  type    = map(string)
  default = { environment = "lab", owner = "engineering", cost_center = "training", managed_by = "terraform" }
}

variable "storage_account_name" {
  type = string
  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Choose a globally unique 3-24-character lowercase storage account name."
  }
}

variable "workspace_name" {
  type    = string
  default = "law-example-operations"
}
variable "backup_writer_principal_id" {
  type    = string
  default = ""
}
variable "enable_recovery_vm" {
  type    = bool
  default = false
}
variable "recovery_subnet_id" {
  type    = string
  default = ""
}
variable "reviewed_vm_image_id" {
  type    = string
  default = ""
}
variable "ssh_public_key" {
  type    = string
  default = ""
}
variable "vm_size" {
  type    = string
  default = "Standard_B2s"
}
