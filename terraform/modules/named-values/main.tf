# Named Values Module for APIM Configuration

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
  }
}

# Active backend pool identifier
resource "azurerm_api_management_named_value" "active_backend" {
  name                = "doc-active-backend"
  resource_group_name = var.resource_group_name
  api_management_name = var.apim_name
  display_name        = "doc-active-backend"
  value               = var.active_backend
  secret              = false
  
  tags = ["backend", "configuration"]
}

# Backend switch latency threshold (seconds)
resource "azurerm_api_management_named_value" "backend_switch_threshold" {
  name                = "backend-switch-threshold"
  resource_group_name = var.resource_group_name
  api_management_name = var.apim_name
  display_name        = "Backend Switch Latency Threshold"
  value               = tostring(var.backend_switch_threshold)
  secret              = false
  
  tags = ["backend", "threshold", "configuration"]
}

# Circuit breaker error rate threshold (percentage)
resource "azurerm_api_management_named_value" "circuit_breaker_threshold" {
  name                = "circuit-breaker-threshold"
  resource_group_name = var.resource_group_name
  api_management_name = var.apim_name
  display_name        = "Circuit Breaker Error Rate Threshold"
  value               = tostring(var.circuit_breaker_threshold)
  secret              = false
  
  tags = ["circuit-breaker", "threshold", "configuration"]
}

# Circuit breaker evaluation timeout (seconds)
resource "azurerm_api_management_named_value" "circuit_breaker_timeout" {
  name                = "circuit-breaker-timeout"
  resource_group_name = var.resource_group_name
  api_management_name = var.apim_name
  display_name        = "Circuit Breaker Evaluation Timeout"
  value               = tostring(var.circuit_breaker_timeout)
  secret              = false
  
  tags = ["circuit-breaker", "timeout", "configuration"]
}

# Azure subscription ID
resource "azurerm_api_management_named_value" "subscription_id" {
  name                = "azure-subscription-id"
  resource_group_name = var.resource_group_name
  api_management_name = var.apim_name
  display_name        = "azure-subscription-id"
  value               = var.subscription_id
  secret              = false
  
  tags = ["azure", "configuration"]
}

# Azure resource group
resource "azurerm_api_management_named_value" "resource_group" {
  name                = "azure-resource-group"
  resource_group_name = var.resource_group_name
  api_management_name = var.apim_name
  display_name        = "azure-resource-group"
  value               = var.resource_group_name
  secret              = false
  
  tags = ["azure", "configuration"]
}

# APIM service name
resource "azurerm_api_management_named_value" "apim_service_name" {
  name                = "azure-apim-service-name"
  resource_group_name = var.resource_group_name
  api_management_name = var.apim_name
  display_name        = "azure-apim-service-name"
  value               = var.apim_name
  secret              = false
  
  tags = ["azure", "configuration"]
}
