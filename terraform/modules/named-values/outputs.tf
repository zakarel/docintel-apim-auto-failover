output "active_backend_id" {
  description = "Named value ID for active backend"
  value       = azurerm_api_management_named_value.active_backend.id
}

output "backend_switch_threshold_id" {
  description = "Named value ID for backend switch threshold"
  value       = azurerm_api_management_named_value.backend_switch_threshold.id
}

output "circuit_breaker_threshold_id" {
  description = "Named value ID for circuit breaker threshold"
  value       = azurerm_api_management_named_value.circuit_breaker_threshold.id
}
