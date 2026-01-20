# Backend Pools Module

This module creates and manages Azure API Management backend pools for Document Intelligence resources with:

- **Priority-based load balancing** across multiple instances
- **Circuit breaker patterns** for common errors (429, 500, 503, 504)
- **Automatic retry logic** with exponential backoff
- **Health monitoring** and automatic failover

## Features

### Circuit Breaker Rules

1. **Server Errors (500-599)**
   - Threshold: 3 errors in 30 seconds
   - Trip duration: 1 minute

2. **Timeouts (408, 504)**
   - Threshold: 5 errors in 30 seconds
   - Trip duration: 1 minute

3. **Rate Limiting (429)**
   - Threshold: 10 errors in 1 minute
   - Trip duration: 2 minutes

### Retry Policy

- **Attempts**: 3 retries
- **Interval**: 1 second
- **Error types**: ServerError, TooManyRequests
- **Status codes**: 408, 429, 500-599

## Usage

```hcl
module "backend_pools" {
  source = "./modules/backend-pools"

  apim_name           = "my-apim-service"
  apim_id             = azurerm_api_management.apim.id
  resource_group_name = "my-resource-group"
  
  west_backends = [
    {
      url      = "https://di-west-1.cognitiveservices.azure.com"
      title    = "DI West Primary"
      priority = 1
    },
    {
      url      = "https://di-west-2.cognitiveservices.azure.com"
      title    = "DI West Secondary"
      priority = 2
    }
  ]
  
  north_backends = [
    {
      url      = "https://di-north-1.cognitiveservices.azure.com"
      title    = "DI North Primary"
      priority = 1
    }
  ]
  
  tags = {
    Environment = "Production"
  }
}
```

## Priority-Based Routing

Lower priority values indicate higher preference. The pool will route to:
1. Priority 1 backends first
2. Priority 2 backends if Priority 1 is unavailable
3. Priority 3 backends if Priority 1 & 2 are unavailable

## Outputs

- `west_pool_id` - Backend pool ID for West region
- `north_pool_id` - Backend pool ID for North region
