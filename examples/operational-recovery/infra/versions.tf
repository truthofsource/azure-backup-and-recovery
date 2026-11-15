terraform {
  required_version = ">= 1.11.0, < 2.0.0"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "4.75.0" }
    azapi   = { source = "Azure/azapi", version = "2.13.0" }

  }
}
provider "azurerm" {
  features {}
  subscription_id                 = var.subscription_id
  resource_provider_registrations = "none"
  storage_use_azuread             = true
}
provider "azapi" { subscription_id = var.subscription_id }
