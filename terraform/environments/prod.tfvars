# Production Environment Configuration
# Configure with your production values - DO NOT commit credentials

subscription_id      = "your-prod-subscription-id"
resource_group_name  = "your-prod-rg-name"
apim_service_name    = "your-prod-apim-service-name"

# API Configuration
api_path = "doc"

# Backend Configuration - Production settings
active_backend            = "doc-west-pool"
backend_switch_threshold  = 5.0
circuit_breaker_threshold = 50
circuit_breaker_timeout   = 30

# West Region Backends (Production with redundancy)
west_backend_endpoints = [
  {
    url      = "https://di-prod-west-primary.cognitiveservices.azure.com"
    title    = "Document Intelligence Prod West Primary"
    priority = 1
  },
  {
    url      = "https://di-prod-west-secondary.cognitiveservices.azure.com"
    title    = "Document Intelligence Prod West Secondary"
    priority = 2
  }
]

# North Region Backends (Production with redundancy)
north_backend_endpoints = [
  {
    url      = "https://di-prod-north-primary.cognitiveservices.azure.com"
    title    = "Document Intelligence Prod North Primary"
    priority = 1
  },
  {
    url      = "https://di-prod-north-secondary.cognitiveservices.azure.com"
    title    = "Document Intelligence Prod North Secondary"
    priority = 2
  }
]

# Tags
tags = {
  Environment = "Production"
  Solution    = "APIM-DocumentIntelligence"
  ManagedBy   = "Terraform"
  CostCenter  = "Production"
  Compliance  = "Required"
}
