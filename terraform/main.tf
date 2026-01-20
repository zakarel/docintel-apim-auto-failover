# Azure API Management Document Intelligence Solution
# Main Terraform Configuration

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
  }

  # Backend configuration for state management
  # Uncomment and configure for production use
  # backend "azurerm" {
  #   resource_group_name  = "terraform-state-rg"
  #   storage_account_name = "tfstatexxxxx"
  #   container_name       = "tfstate"
  #   key                  = "apim-doc-intel.tfstate"
  # }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# Data source for existing APIM service
data "azurerm_api_management" "apim" {
  name                = var.apim_service_name
  resource_group_name = var.resource_group_name
}

# Document Intelligence Backend Pools
module "backend_pools" {
  source = "./modules/backend-pools"

  apim_name           = data.azurerm_api_management.apim.name
  apim_id             = data.azurerm_api_management.apim.id
  resource_group_name = var.resource_group_name
  
  west_backends       = var.west_backend_endpoints
  north_backends      = var.north_backend_endpoints
  
  tags = var.tags
}

# Named Values Configuration
module "named_values" {
  source = "./modules/named-values"

  apim_name           = data.azurerm_api_management.apim.name
  resource_group_name = var.resource_group_name
  subscription_id     = var.subscription_id
  
  active_backend             = var.active_backend
  backend_switch_threshold   = var.backend_switch_threshold
  circuit_breaker_threshold  = var.circuit_breaker_threshold
  circuit_breaker_timeout    = var.circuit_breaker_timeout
  
  tags = var.tags
}

# Document Intelligence API
module "document_intelligence_api" {
  source = "./modules/api"

  apim_name           = data.azurerm_api_management.apim.name
  apim_id             = data.azurerm_api_management.apim.id
  resource_group_name = var.resource_group_name
  
  api_path            = var.api_path
  
  depends_on = [
    module.backend_pools,
    module.named_values
  ]
}

# API Policies
module "api_policies" {
  source = "./modules/policies"

  apim_name                  = data.azurerm_api_management.apim.name
  resource_group_name        = var.resource_group_name
  api_name                   = module.document_intelligence_api.api_name
  
  west_pool_id               = module.backend_pools.west_pool_id
  north_pool_id              = module.backend_pools.north_pool_id
  
  depends_on = [
    module.document_intelligence_api
  ]
}
