# Terraform Outputs for APIM Document Intelligence Solution

output "apim_gateway_url" {
  description = "APIM Gateway URL"
  value       = data.azurerm_api_management.apim.gateway_url
}

output "api_endpoint" {
  description = "Full API endpoint URL"
  value       = "${data.azurerm_api_management.apim.gateway_url}/${var.api_path}"
}

output "west_pool_id" {
  description = "Backend pool ID for West region"
  value       = module.backend_pools.west_pool_id
}

output "north_pool_id" {
  description = "Backend pool ID for North region"
  value       = module.backend_pools.north_pool_id
}

output "active_backend" {
  description = "Currently active backend pool"
  value       = var.active_backend
}

output "backend_switch_threshold" {
  description = "Configured backend switch threshold in seconds"
  value       = var.backend_switch_threshold
}

output "api_name" {
  description = "Name of the deployed API"
  value       = module.document_intelligence_api.api_name
}

output "api_id" {
  description = "ID of the deployed API"
  value       = module.document_intelligence_api.api_id
}
