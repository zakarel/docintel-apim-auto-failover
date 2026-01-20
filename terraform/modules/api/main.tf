# Document Intelligence API Module

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
  }
}

# Document Intelligence API
resource "azurerm_api_management_api" "document_intelligence" {
  name                = "document-intelligence"
  resource_group_name = var.resource_group_name
  api_management_name = var.apim_name
  revision            = "1"
  display_name        = "Azure AI Document Intelligence (proxy)"
  path                = var.api_path
  protocols           = ["https"]
  service_url         = "https://placeholder.cognitiveservices.azure.com"
  
  subscription_required = true
  
  import {
    content_format = "openapi+json"
    content_value  = file("${path.module}/api-definition.json")
  }
}

# Analyze operation
resource "azurerm_api_management_api_operation" "analyze" {
  operation_id        = "post-documentintelligence-documentmodels-modelid-analyze"
  api_name            = azurerm_api_management_api.document_intelligence.name
  api_management_name = var.apim_name
  resource_group_name = var.resource_group_name
  display_name        = "Analyze Document"
  method              = "POST"
  url_template        = "/documentintelligence/documentModels/{modelId}:analyze"
  description         = "Analyze Document"
  
  template_parameter {
    name      = "modelId"
    required  = true
    type      = "string"
    values    = ["prebuilt-invoice"]
    default_value = "prebuilt-invoice"
  }
  
  request {
    query_parameter {
      name      = "api-version"
      required  = true
      type      = "string"
      values    = ["2024-11-30"]
      default_value = "2024-11-30"
    }
    
    query_parameter {
      name     = "_overload"
      required = false
      type     = "string"
      values   = ["analyzeDocument"]
    }
    
    query_parameter {
      name     = "pages"
      required = false
      type     = "string"
    }
    
    query_parameter {
      name     = "locale"
      required = false
      type     = "string"
    }
    
    representation {
      content_type = "application/json"
    }
  }
  
  response {
    status_code = 202
    description = "Accepted"
    
    representation {
      content_type = "application/json"
    }
  }
  
  response {
    status_code = 400
    description = "Bad Request"
  }
  
  response {
    status_code = 401
    description = "Unauthorized"
  }
  
  response {
    status_code = 429
    description = "Too Many Requests"
  }
}

# Analyze Results operation
resource "azurerm_api_management_api_operation" "analyze_results" {
  operation_id        = "analyzeResults"
  api_name            = azurerm_api_management_api.document_intelligence.name
  api_management_name = var.apim_name
  resource_group_name = var.resource_group_name
  display_name        = "analyzeResults"
  method              = "GET"
  url_template        = "/documentintelligence/documentModels/{modelId}/analyzeResults/{resultId}"
  description         = "Get analysis results"
  
  template_parameter {
    name     = "modelId"
    required = true
    type     = "string"
  }
  
  template_parameter {
    name     = "resultId"
    required = true
    type     = "string"
  }
  
  request {
    query_parameter {
      name      = "api-version"
      required  = true
      type      = "string"
      values    = ["2024-11-30"]
    }
  }
  
  response {
    status_code = 200
    description = "Success"
    
    representation {
      content_type = "application/json"
    }
  }
}
