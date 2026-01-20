output "api_policy_id" {
  description = "ID of the API-level policy"
  value       = azurerm_api_management_api_policy.api_level.id
}

output "analyze_policy_id" {
  description = "ID of the analyze operation policy"
  value       = azurerm_api_management_api_operation_policy.analyze.id
}

output "analyze_results_policy_id" {
  description = "ID of the analyze results operation policy"
  value       = azurerm_api_management_api_operation_policy.analyze_results.id
}
