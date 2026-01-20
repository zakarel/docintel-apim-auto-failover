# API Policies Module
# Deploys enhanced APIM policies with circuit breaker protection

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
  }
}

# API-level policy
resource "azurerm_api_management_api_policy" "api_level" {
  api_name            = var.api_name
  api_management_name = var.apim_name
  resource_group_name = var.resource_group_name
  
  xml_content = templatefile("${path.module}/templates/api-level-policy.xml", {
    west_pool_id  = var.west_pool_id
    north_pool_id = var.north_pool_id
  })
}

# Analyze operation policy (POST)
resource "azurerm_api_management_api_operation_policy" "analyze" {
  api_name            = var.api_name
  api_management_name = var.apim_name
  resource_group_name = var.resource_group_name
  operation_id        = "post-documentintelligence-documentmodels-modelid-analyze"
  
  xml_content = file("${path.module}/templates/analyze-operation-policy.xml")
}

# Analyze Results operation policy (GET)
resource "azurerm_api_management_api_operation_policy" "analyze_results" {
  api_name            = var.api_name
  api_management_name = var.apim_name
  resource_group_name = var.resource_group_name
  operation_id        = "analyzeResults"
  
  xml_content = templatefile("${path.module}/templates/analyze-results-operation-policy.xml", {
    west_pool_id  = var.west_pool_id
    north_pool_id = var.north_pool_id
  })
}
