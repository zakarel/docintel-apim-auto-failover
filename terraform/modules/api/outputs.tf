output "api_name" {
  description = "Name of the deployed API"
  value       = azurerm_api_management_api.document_intelligence.name
}

output "api_id" {
  description = "ID of the deployed API"
  value       = azurerm_api_management_api.document_intelligence.id
}

output "api_path" {
  description = "API base path"
  value       = azurerm_api_management_api.document_intelligence.path
}

output "analyze_operation_id" {
  description = "Operation ID for analyze endpoint"
  value       = azurerm_api_management_api_operation.analyze.operation_id
}

output "analyze_results_operation_id" {
  description = "Operation ID for analyze results endpoint"
  value       = azurerm_api_management_api_operation.analyze_results.operation_id
}
