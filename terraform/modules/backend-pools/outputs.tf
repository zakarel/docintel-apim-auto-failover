output "west_pool_id" {
  description = "Backend pool ID for West region"
  value       = azurerm_api_management_backend.west_pool.name
}

output "north_pool_id" {
  description = "Backend pool ID for North region"
  value       = azurerm_api_management_backend.north_pool.name
}

output "west_pool_name" {
  description = "Backend pool name for West region"
  value       = azurerm_api_management_backend.west_pool.name
}

output "north_pool_name" {
  description = "Backend pool name for North region"
  value       = azurerm_api_management_backend.north_pool.name
}
