# Development Environment Configuration
# Copy from .env.sample and configure with your development values

subscription_id      = "your-subscription-id-here"
resource_group_name  = "your-rg-name-here"
apim_service_name    = "your-apim-service-name-here"

# API Configuration
api_path = "doc"

# Backend Configuration
active_backend            = "doc-west-pool"
backend_switch_threshold  = 5.0
circuit_breaker_threshold = 50
circuit_breaker_timeout   = 30

# West Region Backends (Development)
west_backend_endpoints = [
  {
    url      = "https://di-dev-west-primary.cognitiveservices.azure.com"
    title    = "Document Intelligence Dev West Primary"
    priority = 1
  }
]

# North Region Backends (Development)
north_backend_endpoints = [
  {
    url      = "https://di-dev-north-primary.cognitiveservices.azure.com"
    title    = "Document Intelligence Dev North Primary"
    priority = 1
  }
]

# Tags
tags = {
  Environment = "Development"
  Solution    = "APIM-DocumentIntelligence"
  ManagedBy   = "Terraform"
  CostCenter  = "Engineering"
}
